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
                   buoc3_tham_dinh='dat', buoc4_dinh_gia='dat',
                   phieu_ok=True, bien_an_toan_ok=True)
        with patch.dict(screener.LOC, gia_tren_ma200=False):
            self.assertTrue(screener.buy_checklist(row)['buy_ready'])

    # ---------------------------------------------- Giai doan 2 (04/10/2026)
    def test_rs_and_atr_no_longer_filter(self):
        # Quyet dinh 5: RS va ATR da bo o Tang 1; thieu RS (lich su < 273 phien)
        # khong con loai ma neu da co MA200.
        row = dict(tov=20e9, gia=110, ma200=100, ma50=105, rs_252_skip21=-0.3, atr=0.12)
        self.assertTrue(screener.buy_checklist(dict(row))['qua_loc_cung'])
        self.assertTrue(screener.buy_checklist(dict(row, rs_252_skip21=None))['qua_loc_cung'])
        with patch.dict(screener.LOC, rs_252_duong=True, atr_max=0.06):
            self.assertFalse(screener.buy_checklist(dict(row))['qua_loc_cung'])

    def tru2(self, gia, **kw):
        v = td(phieu_ket_qua='DAT', phieu_het_han='2026-12-12',
               than_trong=42.0, co_so=51.0, can_dung_lai=False)
        v.update(kw)
        r = dict(ma='A', gia=gia, tov=20e9, ma200=gia * 0.8, ma50=gia * 0.9,
                 rs_252_skip21=0.0, atr=0.02)
        with patch.dict(screener.os.environ, {'NGAY_CHAY': '2026-10-05'}):
            screener.cua_ro(r, {'A': v}, ro())
        return screener.buy_checklist(r)

    def test_buy_needs_phieu_dat_and_margin_of_safety(self):
        # Quyet dinh 6-9 (sua 18/10, muc 15.8): phieu DAT/CHO con han; gia <= 0,85 x than_trong.
        self.assertTrue(self.tru2(35_700)['buy_ready'])          # = 0,85 x 42.000
        self.assertFalse(self.tru2(35_800)['buy_ready'])         # bien < 15%
        self.assertTrue(self.tru2(30_000, phieu_ket_qua='CHO')['buy_ready'])
        self.assertFalse(self.tru2(30_000, phieu_ket_qua='PHU QUYET')['buy_ready'])
        self.assertFalse(self.tru2(30_000, phieu_het_han='2026-10-04')['buy_ready'])
        self.assertFalse(self.tru2(30_000, phieu_ket_qua=None)['buy_ready'])
        self.assertFalse(self.tru2(30_000, than_trong=None)['buy_ready'])
        self.assertFalse(self.tru2(30_000, can_dung_lai=True)['buy_ready'])
        r = self.tru2(30_000, than_trong=60.0)                   # than_trong > co_so
        self.assertFalse(r['buy_ready'])
        self.assertIn('MAU THUAN', r['ly_do_bien'])

    def test_sell_on_base_value_and_rs_rule_removed(self):
        base = dict(gia=110, ma200=100, rs_252_skip21=-0.5, trong_ro_co_ban=True)
        r = screener.sell_checklist(dict(base, co_so=110))
        self.assertTrue(r['sell_ready'])
        self.assertIn(('cham_co_so', True), r['sell_checklist'])
        self.assertNotIn('rs_12m_below_minus_5pct', [n for n, _ in r['sell_checklist']])
        r = screener.sell_checklist(dict(base, co_so=None))      # RS te van giu
        self.assertFalse(r['sell_ready'])
        self.assertTrue(r['thieu_co_so'])
        self.assertTrue(screener.sell_checklist(dict(base, gia=96, co_so=None))['sell_ready'])

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

    @staticmethod
    def che_do(ten):
        if ten is None:
            return None
        return dict(che_do=ten, ngay='2026-10-02', dong_cua=1737.71, ma200=1795.65,
                    nguong_vao_giam=1741.78, nguong_ra_giam=1795.65)

    def run_plan(self, holdings, cash, candidates, cfg=None, hom_nay='2026-10-02',
                 ro_co_ban=None, che_do='TANG', loai_ky='soat', phieu=()):
        output = io.StringIO()
        with patch.object(allocator, 'HOM_NAY', hom_nay), \
                patch.object(allocator, 'PORTFOLIOS', {'TEST': dict(
                cfg or self.cfg, ten='test', von_ban_dau=100_000)}), \
                patch.object(allocator, 'HOLDINGS', {'TEST': holdings}), \
                patch.object(allocator, 'TIEN_MAT', {'TEST': cash}), \
                patch.object(allocator, 'newest', return_value='unused.json'), \
                patch.object(allocator, 'nap_ro', return_value=ro_co_ban or ro()), \
                patch.object(allocator, 'nap_che_do', return_value=self.che_do(che_do)), \
                patch.object(allocator, 'LOAI_KY', loai_ky), \
                patch.object(allocator, 'PHIEU_LENH', list(phieu)), \
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

    def test_basket_not_closed_blocks_buys_but_not_price_sells(self):
        # 04/10/2026 (muc 14): ro chua chot khong con dung han allocator — lenh
        # BAN theo luat gia/che do van phai sinh ra (che do GIAM ban ca khi ro
        # chua chot), chi lenh MUA bi chan.
        old = self.candidate('OLD', price=70, buy_ready=False, trong_ro_co_ban=None)
        output = self.run_plan([('OLD', 100, 100)], 100_000,
                               [self.candidate('NEW'), old],
                               ro_co_ban=ro(ngay_chot=None))
        self.assertNotIn('  MUA ', output)
        self.assertIn('ro co ban chua chot', output)
        self.assertIn('cham chan cung -25%', output)

    # ---------------------------------------------- Giai doan 2 (04/10/2026)
    def test_bear_regime_sells_everything_and_blocks_buys(self):
        # Quyet dinh 1: GIAM -> ban TOAN BO, khong mien tru ma tot.
        old = self.candidate('OLD', buy_ready=True)
        output = self.run_plan([('OLD', 300, 100)], 100_000,
                               [old, self.candidate('NEW', rank=2)], che_do='GIAM')
        self.assertIn('BAN      300 OLD', output)
        self.assertIn('che do GIAM', output)
        self.assertNotIn('  MUA ', output)

    def test_unknown_regime_blocks_buys_without_forced_sale(self):
        old = self.candidate('OLD', buy_ready=False)
        output = self.run_plan([('OLD', 100, 100)], 100_000,
                               [old, self.candidate('NEW', rank=2)], che_do=None)
        self.assertIn('KHONG XAC DINH', output)
        self.assertNotIn('  MUA ', output)
        self.assertNotIn('  BAN ', output)

    def test_regime_ceiling_limits_buys(self):
        # Quyet dinh 3: DIEU_CHINH tran 60%. Dang giu 55.000/100.000 -> lenh mua
        # NEW (muc tieu ~49.000) bi cat con 5.000 = 500 CP x 10.
        cfg = dict(self.cfg, so_vi_the=2, tran_ma=1, tran_nganh=1)
        old = self.candidate('OLD', sector='A', buy_ready=False)
        output = self.run_plan([('OLD', 550, 100)], 45_000,
                               [old, self.candidate('NEW', price=10, sector='B')],
                               cfg=cfg, che_do='DIEU_CHINH')
        self.assertIn('MUA      500 NEW', output)
        output = self.run_plan([('OLD', 550, 100)], 45_000,
                               [old, self.candidate('NEW', price=10, sector='B')],
                               cfg=cfg, che_do='TANG')
        self.assertNotIn('MUA      500 NEW', output)

    def test_trim_to_regime_ceiling(self):
        # TANG -> DIEU_CHINH: giu 100% > tran 60% + bien 3% -> cat 40% moi vi the.
        cfg = dict(self.cfg, tran_ma=1, tran_nganh=1)
        old = self.candidate('OLD', buy_ready=False)
        output = self.run_plan([('OLD', 1000, 100)], 0, [old], cfg=cfg,
                               che_do='DIEU_CHINH')
        self.assertIn('cat ve tran DIEU_CHINH 60%', output)
        self.assertIn('BAN      400 OLD', output)
        output = self.run_plan([('OLD', 620, 100)], 38_000, [old], cfg=cfg,
                               che_do='DIEU_CHINH')                 # trong bien 3%
        self.assertNotIn('  BAN ', output)

    def test_daily_mode_checks_only_daily_rules(self):
        # Quyet dinh 12: MA200 chi o ky soat; gia tri co so xet moi phien; khong mua.
        ma200 = self.candidate('OLD', buy_ready=False, sell_ready=True,
                               sell_checklist=[('close_below_97pct_ma200', True)])
        output = self.run_plan([('OLD', 100, 100)], 100_000,
                               [ma200, self.candidate('NEW', rank=2)], loai_ky='hang_ngay')
        self.assertNotIn('  BAN ', output)
        self.assertNotIn('  MUA ', output)
        co_so = self.candidate('OLD', buy_ready=False, sell_ready=True,
                               sell_checklist=[('cham_co_so', True)])
        output = self.run_plan([('OLD', 100, 100)], 0, [co_so], loai_ky='hang_ngay')
        self.assertIn('BAN      100 OLD', output)

    def test_order_ticket_is_checked(self):
        # Cam ket #5 tr.70: lenh khong co phieu ghi truoc gio dat bi gan co.
        old = self.candidate('OLD', buy_ready=False)
        output = self.run_plan([('OLD', 100, 100)], 0, [old], che_do='GIAM')
        self.assertIn('CHUA CO PHIEU', output)
        phieu = [dict(so=7, ghi_luc='2026-10-01 18:00', ngay_dat='2026-10-02', dm='TEST',
                      chieu='BAN', ma='OLD', kl=100)]
        output = self.run_plan([('OLD', 100, 100)], 0, [old], che_do='GIAM', phieu=phieu)
        self.assertIn('phieu so 7', output)
        self.assertNotIn('CHUA CO PHIEU', output)

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
