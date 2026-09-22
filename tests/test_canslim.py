import datetime as dt
import unittest
from unittest.mock import patch

import canslim as cs
import canslim_backtest as bt
import canslim_data as cd
import lt_screener as screener


def quy(nam, q, lnst, dt_=100.0, hl=None, **kw):
    return dict(nam=nam, quy=q, isa22=lnst, isa3=dt_, bsa78=kw.pop("eq", 1000.0),
                hl=hl or cd.ngay_hieu_luc(nam, q, None), **kw)


def chuoi(lnst_theo_quy, dt_theo_quy=None, bat_dau=2019):
    out = []
    for n, v in enumerate(lnst_theo_quy):
        y, q = bat_dau + n // 4, n % 4 + 1
        out.append(quy(y, q, v, (dt_theo_quy or [100.0] * len(lnst_theo_quy))[n]))
    return out


class NgayHieuLuc(unittest.TestCase):
    def test_public_date_is_never_before_quarter_end_plus_20_days(self):
        self.assertEqual(cd.ngay_hieu_luc(2025, 1, "2025-04-02T00:00:00"),
                         dt.date(2025, 4, 20))
        self.assertEqual(cd.ngay_hieu_luc(2025, 1, "2025-04-29T00:00:00"),
                         dt.date(2025, 4, 29))

    def test_missing_public_date_uses_legal_lag(self):
        self.assertEqual(cd.ngay_hieu_luc(2025, 2, None), dt.date(2025, 8, 14))
        self.assertEqual(cd.ngay_hieu_luc(2025, 4, None), dt.date(2026, 3, 31))


class CoBan(unittest.TestCase):
    def test_future_reports_are_invisible(self):
        q = chuoi([10] * 4 + [20] * 4)
        truoc = q[-1]["hl"] - dt.timedelta(days=1)
        self.assertEqual(cs.co_ban(q, [], truoc)["ky"], "Q3/2020")
        self.assertEqual(cs.co_ban(q, [], q[-1]["hl"])["ky"], "Q4/2020")

    def test_c_needs_both_profit_and_revenue_growth(self):
        q = chuoi([10] * 4 + [13] * 4, [100] * 4 + [110] * 4)
        f = cs.co_ban(q, [], dt.date(2030, 1, 1))
        self.assertAlmostEqual(f["lnst_yoy"], 0.30)
        self.assertFalse(f["C"])                       # doanh thu chi +10%
        q = chuoi([10] * 4 + [13] * 4, [100] * 4 + [120] * 4)
        self.assertTrue(cs.co_ban(q, [], dt.date(2030, 1, 1))["C"])

    def test_c_is_false_when_prior_quarter_was_a_loss(self):
        q = chuoi([10, 10, 10, -5, 10, 10, 10, 50])
        self.assertIs(cs.co_ban(q, [], dt.date(2030, 1, 1))["C"], False)

    def test_a_requires_three_years_of_rising_ttm_and_roe(self):
        # TTM: 40 -> 50 -> 60 -> 80 (CAGR 26%, khong nam nao giam), ROE = 80/1000 < 15%
        q = chuoi([10] * 4 + [12.5] * 4 + [15] * 4 + [20] * 4)
        f = cs.co_ban(q, [], dt.date(2030, 1, 1))
        self.assertTrue(f["khong_giam"])
        self.assertAlmostEqual(f["cagr3"], 2 ** (1 / 3) - 1)
        self.assertFalse(f["A"])
        for r in q:
            r["bsa78"] = 400.0
        self.assertTrue(cs.co_ban(q, [], dt.date(2030, 1, 1))["A"])

    def test_a_accepts_a_flat_year_as_no_decline(self):
        # Codex #13: "khong nam nao giam" -> 40, 40, 60, 80 van dat (CAGR 26%)
        q = chuoi([10] * 4 + [10] * 4 + [15] * 4 + [20] * 4)
        for r in q:
            r["bsa78"] = 400.0
        self.assertTrue(cs.co_ban(q, [], dt.date(2030, 1, 1))["A"])

    def test_zero_parent_profit_is_not_replaced_by_total_profit(self):
        # Codex #12
        q = chuoi([0] * 4 + [20] * 4, [100] * 4 + [150] * 4)
        for r in q:
            r["isa20"] = 10.0
        self.assertIs(cs.co_ban(q, [], dt.date(2030, 1, 1))["C"], False)

    def test_bank_detection_ignores_unpublished_reports(self):
        # Codex #14
        nam = [dict(nam=y, quy=4, isa20=100.0, cfa18=10.0, hl=dt.date(y + 1, 3, 31))
               for y in (2022, 2023, 2024)]
        q = chuoi([10] * 8, bat_dau=2023)
        q[-1]["isb27"] = 5.0
        q[-1]["hl"] = dt.date(2031, 1, 1)
        self.assertAlmostEqual(cs.co_ban(q, nam, dt.date(2026, 1, 1))["v3"], 0.10)

    def test_a_is_unknown_without_sixteen_quarters(self):
        q = chuoi([10] * 15)
        self.assertIsNone(cs.co_ban(q, [], dt.date(2030, 1, 1))["A"])

    def test_v3_uses_only_published_years_and_skips_banks(self):
        nam = [dict(nam=y, quy=4, isa20=100.0, cfa18=c, hl=dt.date(y + 1, 3, 31))
               for y, c in ((2022, 10.0), (2023, 20.0), (2024, 30.0), (2025, 900.0))]
        q = chuoi([10] * 4)
        self.assertAlmostEqual(cs.co_ban(q, nam, dt.date(2026, 1, 1))["v3"], 0.20)
        for r in q:
            r["isb27"] = 5.0
        self.assertIsNone(cs.co_ban(q, nam, dt.date(2026, 1, 1))["v3"])


class KetLuan(unittest.TestCase):
    def test_main_branch_hard_gates_and_nsl_score(self):
        r = dict(M=True, C=True, A=True, N=True, S=False, L=True)
        self.assertTrue(cs.ket_luan(r)["qua_3a"])
        self.assertFalse(cs.ket_luan(r)["qua_3a_doi_chung"])
        self.assertFalse(cs.ket_luan(dict(r, M=False))["qua_3a"])
        self.assertFalse(cs.ket_luan(dict(r, L=None))["qua_3a"])   # None = khong qua

    def test_unknown_letters_never_pass(self):
        r = dict(M=None, C=None, A=None, N=None, S=None, L=None)
        self.assertFalse(cs.ket_luan(r)["qua_3a"])


class ViTriNgay(unittest.TestCase):
    lich = __import__("pandas").Index([dt.date(2016, 9, 19), dt.date(2016, 9, 20),
                                       dt.date(2026, 9, 22)])

    def test_date_before_history_is_rejected_not_mapped_to_last_session(self):
        # Codex luc dung: get_indexer tra -1 -> iloc[-1] = phien CUOI (du lieu tuong lai)
        with self.assertRaises(ValueError):
            cs.vi_tri_ngay(self.lich, dt.date(2016, 9, 18))

    def test_date_after_history_is_rejected_for_forward_lookup(self):
        with self.assertRaises(ValueError):
            cs.vi_tri_ngay(self.lich, dt.date(2026, 9, 23), method="bfill")

    def test_non_trading_day_pads_back_to_prior_session(self):
        self.assertEqual(cs.vi_tri_ngay(self.lich, dt.date(2020, 1, 1)), 1)


class GioiHan(unittest.TestCase):
    def test_caps_are_reapplied_after_the_no_trade_band(self):
        # Codex #2: sau bien 3% khong duoc vuot tran ma / tong giai ngan
        w = bt.gioi_han({"A": 0.23, "B": 0.20, "C": 0.20, "D": 0.20, "E": 0.20})
        self.assertLessEqual(max(w.values()), bt.TRAN + 1e-12)
        self.assertLessEqual(sum(w.values()), 0.98 + 1e-12)


class NeweyWest(unittest.TestCase):
    def test_zero_lag_matches_plain_t(self):
        x = [0.01, -0.02, 0.03, 0.0, 0.02, 0.01, -0.01]
        import statistics as st
        t_plain = st.mean(x) / (st.pstdev(x) / len(x) ** 0.5)
        self.assertAlmostEqual(bt.nw_t(x, lag=0)[0], t_plain)


class ScreenerGate(unittest.TestCase):
    row = dict(tov=20e9, gia=110, ma200=100, ma50=105, rs_252_skip21=0.1, atr=0.02,
               buoc3_tham_dinh="dat", buoc4_dinh_gia="dat", canslim_3a=False)

    def test_switch_off_does_not_block(self):
        with patch.object(screener, "CANSLIM_CHAN_MUA", False):
            self.assertTrue(screener.buy_checklist(dict(self.row))["buy_ready"])

    def test_switch_on_blocks_failed_or_missing_3a(self):
        with patch.object(screener, "CANSLIM_CHAN_MUA", True):
            self.assertFalse(screener.buy_checklist(dict(self.row))["buy_ready"])
            self.assertFalse(screener.buy_checklist(
                dict(self.row, canslim_3a=None))["buy_ready"])
            self.assertTrue(screener.buy_checklist(
                dict(self.row, canslim_3a=True))["buy_ready"])


if __name__ == "__main__":
    unittest.main()
