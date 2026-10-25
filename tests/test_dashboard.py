"""Kiem lop du lieu cua dashboard/ tren cac file da chot 04-05/10/2026 — khong can mang.

Moc doi chieu: candidates_20261004 / che_do_20261004 (screener ngay 04/10, phien 02/10),
ke_hoach_20261005 (allocator nhip hang ngay), so_giao_dich.json (NAV 18/09 va 05/10).
"""

import json
import unittest
from datetime import date

import pandas as pd

try:
    import streamlit  # noqa: F401
except ImportError:      # python he thong khong co streamlit -> chay bang .venv
    raise unittest.SkipTest("can .venv cua dashboard (requirements.txt)")

from dashboard import danh_muc, nganh, nguon, pheu, thi_truong, ui, vi_mo  # noqa: E402
import lt_che_do  # noqa: E402


def phien(ngay):
    return next(p for p in nguon.danh_sach_phien() if p.ngay == ngay)


class PhienTests(unittest.TestCase):
    def test_khoa_theo_ngay_du_lieu_khong_theo_ten_file(self):
        p = phien("2026-10-02")
        self.assertEqual(p.scan.name, "scan_20261004.json")
        self.assertEqual(p.candidates.name, "candidates_20261004.json")
        self.assertEqual(p.file_che_do.name, "che_do_20261004.json")
        self.assertEqual(phien("2026-09-30").scan.name, "scan_20261001.json")

    def test_bo_qua_ban_quet_tradingview_khong_co_meta(self):
        self.assertTrue(all(p.ngay >= "2026-09-30" for p in nguon.danh_sach_phien()))

    def test_phien_thieu(self):
        ds = [p for p in nguon.danh_sach_phien() if p.ngay <= "2026-10-02"]
        gd = ["2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02", "2026-10-05"]
        self.assertEqual(nguon.phien_thieu(ds, gd), ["2026-10-01", "2026-10-05"])

    def test_bang_lenh_map_theo_ngay_du_lieu(self):
        kh = nguon.danh_sach_ke_hoach()["2026-10-02"]
        self.assertEqual(kh[0].name, "ke_hoach_20261005.txt")
        self.assertEqual((kh[1], kh[2]), ("2026-10-05", "HANG NGAY"))


class CheDoVaPheuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = phien("2026-10-02")
        cls.bq = nguon.doc_ban_quet(cls.p)
        cls.cands = nguon.doc_candidates(cls.p)
        cls.cd = nguon.doc_che_do(cls.p, cls.bq.phu)

    def test_che_do_file_khop_phat_lai(self):
        """File screener ghi va ham lt_che_do tren cung ban quet phai ra cung ket qua."""
        self.assertEqual(self.cd["che_do"], "GIAM")
        lai = lt_che_do.tu_ban_quet(self.bq.phu)
        for k in ("che_do", "dong_cua", "ma200", "nguong_ra_giam", "phien_phan_phoi"):
            self.assertEqual(lai[k], self.cd[k], k)

    def test_chuoi_vnindex_khop_che_do_va_phan_phoi(self):
        vn = thi_truong.chuoi_vnindex(self.bq.phu)
        self.assertEqual(vn["che_do"].iloc[-1], "GIAM")
        self.assertEqual(int(vn["phan_phoi_cua_so"].sum()), self.cd["phien_phan_phoi"])
        self.assertAlmostEqual(vn["ma200"].iloc[-1], self.cd["ma200"], places=1)
        self.assertEqual(sorted(vn.loc[vn["phan_phoi_cua_so"], "ngay"].dt.strftime("%Y-%m-%d")),
                         self.cd["ngay_phan_phoi"])

    def test_pheu_doc_nguyen_candidates(self):
        tang = pheu.cac_tang(self.cands, self.bq, self.cd)
        self.assertEqual(len(tang[0][1]), len(self.bq.df))
        self.assertEqual(len(tang[1][1]), sum(1 for c in self.cands if c["qua_loc_cung"]))
        self.assertEqual([len(t[1]) for t in tang[2:]], [0, 0, 0, 0])

    def test_ly_do_loc_cung_khop_candidates(self):
        """Goi lai build_rows cua screener tren ban quet: tap qua loc cung phai trung file."""
        lydo = pheu.ly_do_loc_cung(self.bq)
        may = {m for m, v in lydo.items() if v == ""}
        file_ = {c["ma"] for c in self.cands if c["qua_loc_cung"]}
        self.assertEqual(may, file_)

    def test_che_do_giam_chan_tang_cuoi(self):
        gia = [dict(c, buy_ready=True, phieu_ok=True, trong_ro_co_ban=True, qua_loc_cung=True)
               for c in self.cands[:2]]
        tang = pheu.cac_tang(gia, self.bq, {"che_do": "GIAM"})
        self.assertEqual(len(tang[4][1]), 2)
        self.assertEqual(tang[5][1], [])
        self.assertEqual(len(pheu.cac_tang(gia, self.bq, {"che_do": "TANG"})[5][1]), 2)

    def test_nganh_phu_moi_ma_co_icb(self):
        b = nganh.bang_nganh(self.bq.df, frozenset(), 0.0)
        co_icb = self.bq.df["icb"].isin(nganh.TEN_ICB)
        self.assertEqual(int(b["Số mã"].sum()), int(co_icb.sum()) + int((~co_icb).sum()))
        self.assertEqual(set(self.bq.df["icb"].dropna()) - set(nganh.TEN_ICB), set())

    def test_do_rong_dem_khong_khop_rieng(self):
        dr = thi_truong.do_rong(self.bq.df, 0.0).loc["Toàn thị trường"]
        self.assertEqual(dr["Số mã"], len(self.bq.df))
        self.assertEqual(dr["Không khớp"], int(self.bq.df["lech_ngay"].sum()))
        self.assertLessEqual(dr["Tăng"] + dr["Giảm"] + dr["Đứng"], dr["Số mã"] - dr["Không khớp"])


class DanhMucTests(unittest.TestCase):
    def setUp(self):
        self.so = nguon.doc_so_giao_dich()

    def test_ngay_mo_ho_trong_so(self):
        self.assertEqual(danh_muc.chuan_ngay("truoc 17/08"), "2026-08-16")
        self.assertEqual(danh_muc.chuan_ngay("17-19/08"), "2026-08-19")
        self.assertEqual(danh_muc.chuan_ngay("2026-09-22"), "2026-09-22")

    def test_nav_05_10_khop_so(self):
        nav = danh_muc.nav_tai("2026-10-05", {"MSB": 14050}, self.so)
        self.assertEqual(nav, self.so["tong_ket"]["chot_05_10"]["nav"])

    def test_nav_18_09_lech_dung_241_dong_ngoai_so(self):
        """So dung tien mat sao ke (gom lai tien gui/phi le) -> lech 241 d, da giai thich."""
        gia = {"MSB": 12900, "BSR": 30200, "VHM": 71000, "DHC": 36550}
        nav = danh_muc.nav_tai("2026-09-18", gia, self.so)
        lech = self.so["tong_ket"]["nav_dung_lai"] - nav
        self.assertEqual(lech, self.so["doi_chieu_sao_ke_18_09"]["lech"])

    def test_vi_the_cuoi_khop_holdings(self):
        import lt_config
        cuoi = danh_muc.su_kien_theo_ngay(self.so)[-1][0]
        vt, tien = danh_muc.trang_thai(cuoi, self.so)
        self.assertEqual(vt, {ma: kl for ma, kl, _ in lt_config.HOLDINGS["DM2"]})
        self.assertEqual(tien, lt_config.TIEN_MAT["DM2"])

    def test_nav_16_10_het_vi_the_msb(self):
        vt, tien = danh_muc.trang_thai("2026-10-16", self.so)
        self.assertEqual(vt, {})
        self.assertEqual(tien, self.so["tong_ket"]["chot_16_10"]["nav"])
        self.assertEqual(danh_muc.nav_tai("2026-10-16", {}, self.so), 61_870_918)

    def test_nav_20_10_khop_sao_ke(self):
        """Tien mat so = sao ke 07/10 + tien ban 16/10 dang cho T+2; lech so cu = -190.000 + 14.768."""
        dc = self.so["doi_chieu_sao_ke_20_10"]
        vt, tien = danh_muc.trang_thai("2026-10-20", self.so)
        self.assertEqual(vt, {})
        self.assertEqual(tien, dc["tien_mat_so_20_10"])
        self.assertEqual(tien, dc["tien_mat_sao_ke_07_10"] + dc["tien_ban_16_10_chua_ve"])
        self.assertEqual(tien - 61_870_918, dc["lech_so_cu_61_870_918"])
        self.assertEqual(tien, self.so["tong_ket"]["chot_20_10"]["nav"])
        ngoai_so = next(e for e in self.so["su_kien_phi_tien_mat"] if e.get("ma") == "DM2_DOI_CHIEU")
        self.assertEqual(sum(ngoai_so["chi_tiet"].values()), ngoai_so["dong_tien"])

    def test_nav_21_10_khop_sao_ke_cuoi_ky(self):
        """Sao ke cuoi ky 21/09-21/10: sau T+2 ngay 20/10 (tru TTLK 42d, lam tron 1d, thue co tuc CP 70.000d) -> 61.625.643."""
        dc = self.so["doi_chieu_sao_ke_cuoi_ky"]
        vt, tien = danh_muc.trang_thai("2026-10-21", self.so)
        self.assertEqual(vt, {})
        self.assertEqual(tien, dc["tien_mat_sao_ke_21_10"])
        self.assertEqual(tien, dc["so_du_dau_ky_tien"] + dc["tong_tang_tien"] - dc["tong_giam_tien"])
        self.assertEqual(tien - 61_695_686, dc["lech_so_20_10_61_695_686"])
        self.assertEqual(tien, self.so["tong_ket"]["chot_21_10"]["nav"])
        sk = next(e for e in self.so["su_kien_phi_tien_mat"] if e.get("ma") == "DM2_SAO_KE_CUOI_KY")
        self.assertEqual(sum(sk["chi_tiet"].values()), sk["dong_tien"])

    def test_lai_lo_da_thuc_hien_gan_so(self):
        ll = danh_muc.lai_lo_da_thuc_hien(self.so)
        self.assertEqual(len(ll), self.so["tong_ket"]["so_lenh_ban"])
        self.assertAlmostEqual(ll["Lãi/lỗ"].sum(), self.so["tong_ket"]["lai_lo_da_thuc_hien_rong"],
                               delta=500)

    def test_chia_tach_trong_so_quy_doi_kl(self):
        """Gia da dieu chinh: MSB truoc 28/08 phai tinh 700 x 1,2 = 840 CP."""
        gia = {"MSB": pd.Series({"2026-08-27": 10_000.0, "2026-08-28": 10_000.0})}
        so = {"von_goc": 0, "giao_dich": [g for g in self.so["giao_dich"] if g["ma"] == "MSB"
                                          and g["ngay"] == "truoc 17/08"],
              "su_kien_phi_tien_mat": self.so["su_kien_phi_tien_mat"]}
        nav = danh_muc.chuoi_nav(gia, ["2026-08-27", "2026-08-28"], so).set_index("ngay")
        self.assertEqual(nav["co_phieu"].tolist(), [8_400_000, 8_400_000])

    def test_su_kien_ngoai_so_do_tu_gia_khop(self):
        """GMD: gia khop ~78.800 so voi gia dieu chinh ~52.300 -> he so ~1,5 toi lenh cuoi."""
        gia = {"GMD": pd.Series({"2026-08-19": 52_400.0, "2026-09-03": 52_000.0}),
               "LPB": pd.Series({"2026-08-19": 50_700.0, "2026-09-03": 48_800.0})}
        hs = danh_muc.he_so_tu_gia_khop(gia, self.so)
        self.assertEqual(set(hs), {"GMD"})
        self.assertAlmostEqual(hs["GMD"][0], 1.5, delta=0.02)
        self.assertEqual(hs["GMD"][1], "2026-09-03")

    def test_doc_bang_lenh_05_10(self):
        L = danh_muc.doc_bang_lenh(nguon.DATA / "ke_hoach_20261005.txt")
        self.assertEqual({(l["Chiều"], l["Mã"], l["KL"]) for l in L["lenh"]},
                         {("BAN", "BSR", 100), ("BAN", "DHC", 200), ("BAN", "MSB", 440)})
        self.assertTrue(all(l["DM"] == "DM2" and l["Phiếu"].startswith("phieu so") for l in L["lenh"]))
        self.assertEqual(len(L["cham_tay"]), 3)
        self.assertIn("che do GIAM", L["khong_mua"][0]["Lý do"])

    def test_lenh_chua_thuc_hien_sau_ban_het_16_10(self):
        from unittest import mock
        import lt_config
        kh_1510 = {"lenh": danh_muc.doc_bang_lenh(nguon.DATA / "ke_hoach_20261015.txt")}
        chua = danh_muc.lenh_chua_thuc_hien(kh_1510, "2026-10-15")
        self.assertEqual(chua, {"lenh": [], "cham_tay": []})
        with mock.patch.dict(lt_config.HOLDINGS, {"DM1": [], "DM2": [("MSB", 140, 13_333)]}), \
             mock.patch.object(lt_config, "PHIEU_LENH", []):
            chua_truoc = danh_muc.lenh_chua_thuc_hien(kh_1510, "2026-10-15")
            self.assertEqual(len(chua_truoc["lenh"]), 1)
            self.assertEqual(len(chua_truoc["cham_tay"]), 1)


class MediciRegimeTests(unittest.TestCase):
    def test_nhan_ms_va_mo_phong_student_t(self):
        import numpy as np
        import medici_regime as mr
        self.assertEqual(mr.nhan_ms([34.0, -61.0], [11.7, 29.5], 2),
                         ["Tăng / Biến động thấp", "Giảm / Biến động cao"])
        self.assertEqual(mr.nhan_ms([35.6, 25.0, -110.0], [15.0, 9.4, 33.7], 3),
                         ["Tăng – sôi động", "Tăng – êm (biến động thấp)", "Giảm/Hoảng loạn"])
        P = np.array([[0.95, 0.05], [0.10, 0.90]])
        scen, gt = mr.mo_phong_kich_ban(1700.0, [0.9, 0.1], np.array([0.1, -0.2]),
                                        np.array([0.5, 3.0]), P, [7, 21], n_sim=5000, nu=5.1)
        self.assertLess(scen[7]["p5"], scen[7]["p50"])
        self.assertLess(scen[7]["p50"], scen[7]["p95"])
        self.assertAlmostEqual(sum(gt[21]), 1.0, places=6)

    def test_chi_so_hieu_qua_vol_bang_0_khong_loi(self):
        import numpy as np
        import medici_regime as mr
        r_const = pd.Series([0.0002] * 250)
        m = mr.chi_so_hieu_qua(r_const, 0.05)
        self.assertTrue(np.isnan(m["Sharpe"]))


class DayGithubTests(unittest.TestCase):
    def test_chi_lay_file_pipeline(self):
        """Nut Day len GitHub chi duoc commit file pipeline — so, tham_dinh, config thi khong."""
        from dashboard import chay
        porcelain = "\n".join([
            " M data/so_giao_dich.json", " M data/tham_dinh.json", "?? data/vi_mo.json",
            "?? data/scan_20261007.json", "?? data/candidates_20261007.json",
            "?? data/che_do_20261007.json", "?? data/ke_hoach_20261007.txt",
            "?? data/bao_cao_dau_tu_20261007.xlsx", "?? data/scan_vietcap_doi_chieu_20260921.json",
            "?? data/lt_config_backup_20261007.py", "?? data/scan_weekly_20260824.json",
            'R  data/x.json -> data/scan_20261008.json', " M lt_config.py"])
        self.assertEqual(chay.loc_file_pipeline(porcelain), [
            "data/bao_cao_dau_tu_20261007.xlsx", "data/candidates_20261007.json",
            "data/che_do_20261007.json", "data/ke_hoach_20261007.txt",
            "data/scan_20261007.json", "data/scan_20261008.json"])

    def test_khong_day_file_bi_xoa(self):
        porcelain = "\n".join([" D data/scan_20261007.json", "D  data/candidates_20261007.json",
                               "?? data/che_do_20261007.json"])
        from dashboard import chay
        self.assertEqual(chay.loc_file_pipeline(porcelain), ["data/che_do_20261007.json"])


class BoChayTests(unittest.TestCase):
    """Bo chay nut quet tren thu muc tam — khong mang, khong dung data/ that."""

    def setUp(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from dashboard import chay
        self.chay = chay
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.cache = self.data / "cache_dashboard"
        self.cache.mkdir()
        for ten, gt in (("DATA", self.data), ("CACHE", self.cache),
                        ("KHOA", self.cache / "dang_chay.lock")):
            p = mock.patch.object(chay, ten, gt)
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def _ke_hoach(self, ten, ngay_cd):
        (self.data / ten).write_text(f"NGAY CHAY 2026-10-09 — nhip HANG NGAY\n"
                                     f"CHE DO THI TRUONG ({ngay_cd}): GIAM\n", encoding="utf-8")

    def test_ke_hoach_bi_chiem_tren_data_that(self):
        from unittest import mock
        with mock.patch.object(self.chay, "DATA", nguon.DATA):
            self.assertEqual(self.chay.ke_hoach_bi_chiem("2026-10-05"), "2026-10-02")
            self.assertEqual(self.chay.ke_hoach_bi_chiem("2026-08-17"), "?")
            self.assertIsNone(self.chay.ke_hoach_bi_chiem("2026-10-08"))
            self.assertIsNone(self.chay.ke_hoach_bi_chiem("2026-10-09"))
            self.assertIsNone(self.chay.ke_hoach_bi_chiem("2026-12-31"))

    def test_bang_lenh_08_10_da_khoi_phuc(self):
        kh = nguon.danh_sach_ke_hoach()
        self.assertEqual(kh["2026-10-08"][0].name, "ke_hoach_20261008.txt")
        self.assertEqual(kh["2026-10-09"][0].name, "ke_hoach_20261009.txt")

    def test_allocator_dat_ten_theo_ngay_du_lieu_va_khong_de_excel_cu(self):
        """Chay ngay 09/10 cho phien 08/10: Excel allocator ghi theo ngay chay -> doi ten theo phien,
        file bao_cao_dau_tu_20261009 cua lan chay khac giu nguyen."""
        from unittest import mock
        cu = self.data / "bao_cao_dau_tu_20261009.xlsx"
        cu.write_bytes(b"phien 09/10")

        def gia_allocator(cmd, env=None, ra=None):
            (self.data / "bao_cao_dau_tu_20261009.xlsx").write_bytes(b"phien 08/10")
            ra.write_text("CHE DO THI TRUONG (2026-10-08)\n", encoding="utf-8")
            return 0, ""

        with mock.patch.object(self.chay, "_chay", gia_allocator):
            rc, _ = self.chay.chay_allocator(self.data / "candidates_20261008.json", "2026-10-09",
                                             "2026-10-08")
        self.assertEqual(rc, 0)
        self.assertEqual((self.data / "bao_cao_dau_tu_20261008.xlsx").read_bytes(), b"phien 08/10")
        self.assertEqual(cu.read_bytes(), b"phien 09/10")
        self.assertTrue((self.data / "ke_hoach_20261008.txt").exists())
        self.assertEqual(list(self.cache.glob("*.cat")), [])

    def test_allocator_khong_ghi_de_bang_lenh_phien_khac(self):
        from unittest import mock
        self._ke_hoach("ke_hoach_20261005.txt", "2026-10-02")
        gia = mock.Mock(return_value=(0, ""))
        with mock.patch.object(self.chay, "_chay", gia):
            rc, _ = self.chay.chay_allocator(self.data / "c.json", "2026-10-05", "2026-10-05")
        self.assertEqual(rc, 1)
        gia.assert_not_called()

    def _gia_quet(self, ngay_that):
        def quet(cmd, env=None, ra=None):
            out = cmd[cmd.index("--ra") + 1]
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"_meta": {"ngay_du_lieu": ngay_that}}, f, separators=(",", ":"))
            return 0, ""
        return quet

    def _hom_nay(self, ngay_moi_nhat, ngay_that):
        from unittest import mock
        with mock.patch.multiple(self.chay, phien_moi_nhat=mock.Mock(return_value=ngay_moi_nhat),
                                 _chay=self._gia_quet(ngay_that),
                                 chay_screener=mock.Mock(return_value=(0, "")),
                                 chay_allocator=mock.Mock(return_value=(0, "")),
                                 vi_mo=mock.Mock(return_value=0),
                                 tai_danh_ba_ma=mock.Mock()):
            return self.chay.hom_nay()

    def test_quet_dat_ten_theo_phien_that(self):
        self.assertEqual(self._hom_nay("2026-10-08", "2026-10-09"), 0)
        self.assertFalse((self.data / "scan_20261008.json").exists())
        self.assertTrue((self.data / "scan_20261009.json").exists())
        self.assertEqual(list(self.cache.glob("*.tam.json")), [])

    def test_quet_khong_de_ban_quet_dung_ten(self):
        """Phien dong cua trong luc quet + scan_<phien that> dang chua phien khac -> dung, khong
        ghi gi vao data/ (truoc day ban quet sai phien nam lai duoi ten scan_<d>)."""
        (self.data / "scan_20261009.json").write_text(
            json.dumps({"_meta": {"ngay_du_lieu": "2026-10-07"}}, separators=(",", ":")),
            encoding="utf-8")
        self.assertEqual(self._hom_nay("2026-10-08", "2026-10-09"), 1)
        self.assertFalse((self.data / "scan_20261008.json").exists())
        self.assertEqual(list(self.cache.glob("*.tam.json")), [])

    def test_khoa_nguyen_tu(self):
        self.assertTrue(self.chay.giu_khoa())
        self.assertFalse(self.chay.giu_khoa())
        import os
        import time
        cu = time.time() - self.chay.KHOA_HET_HAN - 60
        os.utime(self.chay.KHOA, (cu, cu))          # khoa cua tien trinh da chet
        self.assertTrue(self.chay.giu_khoa())


class ViMoVaDinhDangTests(unittest.TestCase):
    def test_vi_mo_vn_chua_nhap_la_cu(self):
        raw = {"chi_so": {"cpi": {"ten": "CPI", "chuoi": []}, "pmi": {"ten": "PMI"}}}
        b = vi_mo.bang_vi_mo_vn(raw)
        self.assertEqual(len(b), 2)
        self.assertTrue(b["Cũ"].all())

    def test_vi_mo_vn_tuoi_nhap(self):
        raw = {"chi_so": {"cpi": {"ten": "CPI", "chuoi": [
            {"ky": "2026-08", "gia_tri": 3.1, "ngay_nhap": "2026-09-06"},
            {"ky": "2026-09", "gia_tri": 3.3, "ngay_nhap": "2026-10-06"}]}}}
        b = vi_mo.bang_vi_mo_vn(raw, hom_nay=date(2026, 10, 7)).iloc[0]
        self.assertEqual((b["Kỳ"], b["Giá trị"], b["Kỳ trước"], b["Số ngày từ khi nhập"], b["Cũ"]),
                         ("2026-09", 3.3, 3.1, 1, False))
        b = vi_mo.bang_vi_mo_vn(raw, hom_nay=date(2026, 12, 1)).iloc[0]
        self.assertTrue(b["Cũ"])

    def test_vi_mo_json_hop_le(self):
        raw = json.loads(nguon.VI_MO_FILE.read_text(encoding="utf-8"))
        for v in raw["chi_so"].values():
            self.assertIn("ten", v)
            self.assertIsInstance(v["chuoi"], list)

    def test_ngay_cuoi_thang_brent(self):
        self.assertTrue(vi_mo.la_ngay_cuoi_thang("2026-09-30"))
        self.assertFalse(vi_mo.la_ngay_cuoi_thang("2026-09-29"))

    def test_so_kieu_viet_nam(self):
        self.assertEqual(ui.so(1737.71, 2), "1.737,71")
        self.assertEqual(ui.so(61778631), "61.778.631")
        self.assertEqual(ui.pt(0.0329), "+3,3%")
        self.assertEqual(ui.pt(-0.0066, 2), "-0,66%")
        self.assertEqual(ui.so(None), "—")
        self.assertEqual(ui.ngay_vn("2026-10-02"), "02/10/2026")


if __name__ == "__main__":
    unittest.main()
