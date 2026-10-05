import contextlib
import io
import unittest
from unittest.mock import patch

import lt_allocator as allocator
import lt_screener as screener
import lt_config


def ro(ngay_chot='2026-10-01', vi_mo='on dinh', nganh=None):
    return {'ngay_chot': ngay_chot, 'vi_mo': {'ket_luan': vi_mo},
            'nganh': nganh if nganh is not None else {'Bank': {'trong_ro': True}}}


def td(**kw):
    base = dict(buoc3='dat', buoc4='dat', luan_diem_con_nguyen=None,
                trong_ro=True, nganh='Bank', uu_tien=None, ly_do_ro='')
    base.update(kw)
    return base


class ScreenerTests(unittest.TestCase):
    def test_disabled_filter_is_respected_by_buy_checklist(self):
        row = dict(tov=20e9, gia=90, ma200=100, ma50=110,
                   rs_252_skip21=0.1, atr=0.02, trong_ro_co_ban=True,
                   buoc3_tham_dinh='dat', buoc4_dinh_gia='dat')
        with patch.dict(screener.LOC, gia_tren_ma200=False):
            self.assertTrue(screener.buy_checklist(row)['buy_ready'])

    def test_trend_basket_alone_is_not_enough_to_buy(self):
        row = dict(tov=20e9, gia=110, ma200=100, ma50=105, rs_252_skip21=0.1,
                   atr=0.02, buoc4_dinh_gia='dat')
        for tt in (None, False):
            r = screener.buy_checklist(dict(row, trong_ro_co_ban=tt))
            self.assertTrue(r['qua_loc_cung'])
            self.assertFalse(r['buy_ready'])

    def test_basket_state_three_values(self):
        t = screener.trang_thai_ro
        self.assertIs(t('A', {'A': td()}, ro())[0], True)
        # nguoi noi "khong" o tang nao cung -> False (ban theo quy tac 4)
        self.assertIs(t('A', {'A': td(trong_ro=False)}, ro())[0], False)
        self.assertIs(t('A', {'A': td()}, ro(nganh={'Bank': {'trong_ro': False}}))[0], False)
        self.assertIs(t('A', {'A': td(luan_diem_con_nguyen=False)}, ro())[0], False)
        self.assertIs(t('A', {'A': td(buoc3='loai')}, ro())[0], False)
        # thieu hoac nhap sai -> None (khong mua, khong tu ban)
        self.assertIsNone(t('A', {'A': td()}, ro(ngay_chot=None))[0])
        self.assertIsNone(t('A', {}, ro())[0])
        self.assertIsNone(t('A', {'A': td(nganh='Typo')}, ro())[0])
        self.assertIsNone(t('A', {'A': td(nganh=None)}, ro())[0])
        self.assertIsNone(t('A', {'A': td()}, ro(vi_mo=''))[0])
        self.assertIsNone(t('A', {'A': td(buoc3='chua')}, ro())[0])

    def test_exit_rule_4_only_on_explicit_false(self):
        base = dict(gia=110, ma200=100, rs_252_skip21=0.1)
        self.assertTrue(screener.sell_checklist(dict(base, trong_ro_co_ban=False))['sell_ready'])
        r = screener.sell_checklist(dict(base, trong_ro_co_ban=None))
        self.assertFalse(r['sell_ready'])
        self.assertTrue(r['thieu_ra_soat_ro'])
        self.assertNotIn('rank_below_40pct', [n for n, _ in r['sell_checklist']])

    def test_short_history_fails_filter_without_crashing(self):
        r = dict(tov=20e9, gia=110, ma200=None, ma50=None, rs_252_skip21=None,
                 atr=0.02, trong_ro_co_ban=True, buoc4_dinh_gia='dat')
        self.assertFalse(screener.buy_checklist(dict(r))['qua_loc_cung'])
        self.assertFalse(screener.sell_checklist(dict(r))['sell_ready'])

    def test_buy_order_is_priority_then_atr(self):
        rows = [dict(ma='A', uu_tien=None, atr=0.01), dict(ma='B', uu_tien=2, atr=0.01),
                dict(ma='C', uu_tien=1, atr=0.05), dict(ma='D', uu_tien=2, atr=0.005)]
        self.assertEqual([r['ma'] for r in sorted(rows, key=screener.thu_tu_mua)],
                         ['C', 'D', 'B', 'A'])


class AllocatorTests(unittest.TestCase):
    cfg = dict(so_vi_the=10, tran_ma=0.15, tran_nganh=0.30,
               ticket_toi_thieu=0)

    def test_sector_cap_is_value_not_number_of_symbols(self):
        chosen = [dict(ma=str(i), nganh='Bank' if i < 3 else 'Other' + str(i),
                       atr=0.01 if i < 3 else 0.06) for i in range(10)]
        weights = allocator.ty_trong(chosen, self.cfg)
        self.assertLessEqual(sum(weights[str(i)] for i in range(3)), 0.30 + 1e-9)
        self.assertLessEqual(max(weights.values()), 0.15 + 1e-9)

    def run_plan(self, holdings, cash, candidates, cfg=None, hom_nay='2026-10-02',
                 ro_co_ban=None):
        output = io.StringIO()
        with patch.object(allocator, 'HOM_NAY', hom_nay), \
                patch.object(allocator, 'PORTFOLIOS', {'TEST': dict(
                cfg or self.cfg, ten='test', von_ban_dau=100_000)}), \
                patch.object(allocator, 'HOLDINGS', {'TEST': holdings}), \
                patch.object(allocator, 'TIEN_MAT', {'TEST': cash}), \
                patch.object(allocator, 'newest', return_value='unused.json'), \
                patch.object(allocator, 'nap_ro', return_value=ro_co_ban or ro()), \
                patch('builtins.open', unittest.mock.mock_open(read_data='[]')), \
                patch.object(allocator.json, 'load', return_value=candidates), \
                patch.object(allocator, 'export_excel'), \
                contextlib.redirect_stdout(output):
            allocator.main()
        return output.getvalue()

    def candidate(self, ma, price=100, sector='Bank', rank=1, **kw):
        c = dict(ma=ma, gia=price, nganh=sector, uu_tien=rank,
                 atr=0.02, rs_252_skip21=0.1, rs_126=0.1, rs_63=0.1,
                 rs_21=0.1, tov=20e9, qua_loc_cung=True, giao_diem=True,
                 trong_ro_co_ban=True, ly_do_ro='', san='HSX',
                 buoc3_tham_dinh='dat', buoc4_dinh_gia='dat',
                 buy_ready=True, sell_ready=False, sell_checklist=[])
        c.update(kw)
        return c

    def test_kept_holdings_cannot_create_unfunded_buy(self):
        output = self.run_plan([('OLD', 1000, 100)], 0,
                               [self.candidate('NEW')])
        self.assertNotIn('  MUA ', output)

    def test_kept_holdings_consume_sector_capacity(self):
        # OLD da roi Tang 1 nhung van co ban ghi (screener ghi moi ma dang giu).
        old = self.candidate('OLD', buy_ready=False, qua_loc_cung=False,
                             giao_diem=False)
        output = self.run_plan([('OLD', 400, 100)], 60_000,
                               [self.candidate('NEW'), old])
        self.assertNotIn('  MUA ', output)

    def test_basket_not_closed_blocks_order_table(self):
        with self.assertRaises(SystemExit):
            self.run_plan([], 100_000, [self.candidate('NEW')],
                          ro_co_ban=ro(ngay_chot=None))

    def test_holding_with_unclear_basket_is_flagged_not_sold(self):
        old = self.candidate('OLD', buy_ready=False, trong_ro_co_ban=None,
                             ly_do_ro='chua co ket luan trong_ro')
        output = self.run_plan([('OLD', 100, 100)], 0, [old])
        self.assertIn('PHAI CHAM TAY', output)
        self.assertNotIn('  BAN ', output)

    def test_exit_rule_4_sells_whole_position(self):
        old = self.candidate('OLD', buy_ready=False, trong_ro_co_ban=False,
                             sell_ready=True,
                             sell_checklist=[('ngoai_ro_co_ban', True)])
        output = self.run_plan([('OLD', 300, 100)], 0, [old])
        self.assertIn('BAN      300 OLD', output)

    def test_hard_stop_uses_price_of_holding_that_left_filter(self):
        # Lo hong muc 10.3: truoc day ma roi loc khong co gia -> lui ve gia von.
        old = self.candidate('OLD', price=70, buy_ready=False, qua_loc_cung=False,
                             giao_diem=False)
        output = self.run_plan([('OLD', 100, 100)], 0, [old])
        self.assertIn('cham chan cung -25%', output)

    def test_buy_deadline(self):
        with patch.dict(allocator.TOP_DOWN, han_chot_lenh_mua={'2026-10-01': '2026-10-05'}):
            self.assertEqual(allocator.han_chot_mua_da_qua('2026-10-05'), '')
            self.assertEqual(allocator.han_chot_mua_da_qua('2026-10-06'), '2026-10-05')
            self.assertEqual(allocator.han_chot_mua_da_qua('2026-11-01'), '')
            self.assertEqual(allocator.han_chot_mua_da_qua('2026-09-30'), '')
        self.assertIn('  MUA ', self.run_plan([], 100_000, [self.candidate('NEW')],
                                              hom_nay='2026-10-05'))
        output = self.run_plan([], 100_000, [self.candidate('NEW')], hom_nay='2026-10-06')
        self.assertIn('QUA HAN CHOT', output)
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
