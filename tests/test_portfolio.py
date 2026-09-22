import contextlib
import io
import unittest
from unittest.mock import patch

import lt_allocator as allocator
import lt_screener as screener
import lt_config


class ScreenerTests(unittest.TestCase):
    def test_equal_values_have_equal_percentiles(self):
        self.assertEqual(screener.pct_rank([1, 2, 2, 3]), [0, 0.5, 0.5, 1])

    def test_tied_scores_do_not_depend_on_input_order(self):
        rows = [dict(ma=ma, **{k: 1 for k in screener.RS_WEIGHTS})
                for ma in ['CCC', 'AAA', 'BBB']]
        a = screener.score([dict(r) for r in rows])
        b = screener.score([dict(r) for r in reversed(rows)])
        self.assertEqual(a, b)
        self.assertEqual(len({r['thu_hang'] for r in a}), 1)

    def test_disabled_filter_is_respected_by_buy_checklist(self):
        row = dict(tov=20e9, gia=90, ma200=100, ma50=110,
                   rs_252_skip21=0.1, atr=0.02,
                   buoc3_tham_dinh='dat', buoc4_dinh_gia='dat')
        with patch.dict(screener.LOC, gia_tren_ma200=False):
            self.assertTrue(screener.buy_checklist(row)['buy_ready'])


class AllocatorTests(unittest.TestCase):
    cfg = dict(so_vi_the=10, tran_ma=0.15, tran_nganh=0.30,
               ticket_toi_thieu=0)

    def test_sector_cap_is_value_not_number_of_symbols(self):
        chosen = [dict(ma=str(i), nganh='Bank' if i < 3 else 'Other' + str(i),
                       atr=0.01 if i < 3 else 0.06) for i in range(10)]
        weights = allocator.ty_trong(chosen, self.cfg)
        self.assertLessEqual(sum(weights[str(i)] for i in range(3)), 0.30 + 1e-9)
        self.assertLessEqual(max(weights.values()), 0.15 + 1e-9)

    def run_plan(self, holdings, cash, candidates, cfg=None):
        output = io.StringIO()
        with patch.object(allocator, 'PORTFOLIOS', {'TEST': dict(
                cfg or self.cfg, ten='test', von_ban_dau=100_000)}), \
                patch.object(allocator, 'HOLDINGS', {'TEST': holdings}), \
                patch.object(allocator, 'TIEN_MAT', {'TEST': cash}), \
                patch.object(allocator, 'newest', return_value='unused.json'), \
                patch('builtins.open', unittest.mock.mock_open(read_data='[]')), \
                patch.object(allocator.json, 'load', return_value=candidates), \
                patch.object(allocator, 'export_excel'), \
                contextlib.redirect_stdout(output):
            allocator.main()
        return output.getvalue()

    def candidate(self, ma, price=100, sector='Bank', rank=1):
        return dict(ma=ma, gia=price, nganh=sector, thu=rank, diem=1,
                    atr=0.02, rs_252_skip21=0.1, rs_126=0.1, rs_63=0.1,
                    rs_21=0.1, trend_r2=1, tov=20e9, qua_loc_cung=True,
                    buoc3_tham_dinh='dat', buoc4_dinh_gia='dat',
                    buy_ready=True, sell_ready=False, sell_checklist=[])

    def test_kept_holdings_cannot_create_unfunded_buy(self):
        output = self.run_plan([('OLD', 1000, 100)], 0,
                               [self.candidate('NEW')])
        self.assertNotIn('  MUA ', output)

    def test_kept_holdings_consume_sector_capacity(self):
        # OLD is absent from candidates; use the configured sector map.
        with patch.dict(lt_config.NGANH, OLD='Bank'):
            output = self.run_plan([('OLD', 400, 100)], 60_000,
                                   [self.candidate('NEW')])
        self.assertNotIn('  MUA ', output)

    def test_review_log_uses_simulated_date(self):
        order = dict(dm='DM2', ma='AAA', gia_han_den='2099-09-30',
                     ngay_ghi_gia_han='2099-09-16')
        output = io.StringIO()
        with patch.object(allocator, 'HOM_NAY', '2099-09-21'), \
                patch.object(allocator, 'LENH_QUY_TAC_5', [order]), \
                contextlib.redirect_stdout(output):
            allocator.in_lenh_quy_tac_5()
        self.assertNotIn('GIA HAN KHONG HOP LE', output.getvalue())

    def test_buy_budget_includes_fees_and_rank_priority(self):
        candidates = {ma: self.candidate(ma, sector=ma, rank=i)
                      for i, ma in enumerate(['AAA', 'BBB'])}
        cfg = dict(self.cfg, tran_ma=1, tran_nganh=1)
        allowed, reduced = allocator.gioi_han_mua(
            {'BBB': 100, 'AAA': 100}, {}, {}, 20_000,
            {'AAA': 100, 'BBB': 100}, candidates, cfg, 20_000)
        self.assertEqual(allowed, {'AAA': 100})
        self.assertEqual(reduced, {'BBB': 100})

    def test_sales_fund_buys_net_of_fees(self):
        cfg = dict(self.cfg, tran_ma=1, tran_nganh=1)
        allowed, _ = allocator.gioi_han_mua(
            {'NEW': 200}, {'OLD': 200}, {'OLD': 200}, 0,
            {'NEW': 100, 'OLD': 100}, {'NEW': self.candidate('NEW')},
            cfg, 20_000)
        self.assertEqual(allowed, {'NEW': 100})

    def test_retained_positions_consume_slots(self):
        cfg = dict(self.cfg, so_vi_the=1, tran_ma=1, tran_nganh=1)
        output = self.run_plan([('OLD', 100, 100)], 90_000,
                               [self.candidate('NEW')], cfg)
        self.assertNotIn('  MUA ', output)

    def test_new_position_below_minimum_ticket_is_not_opened(self):
        cfg = dict(self.cfg, ticket_toi_thieu=15_000, tran_ma=1, tran_nganh=1)
        allowed, _ = allocator.gioi_han_mua(
            {'NEW': 200}, {}, {}, 12_000, {'NEW': 100},
            {'NEW': self.candidate('NEW')}, cfg, 100_000)
        self.assertEqual(allowed, {})

    def test_existing_odd_lot_top_up_is_preserved(self):
        allowed, _ = allocator.gioi_han_mua(
            {'NEW': 50}, {}, {'NEW': 50}, 95_000, {'NEW': 100},
            {'NEW': self.candidate('NEW')}, self.cfg, 100_000)
        self.assertEqual(allowed, {'NEW': 50})


if __name__ == '__main__':
    unittest.main()
