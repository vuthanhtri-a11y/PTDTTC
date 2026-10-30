"""Lop mang cua lt_scan_vietcap.py — chay offline, gia lap Vietcap chan (418) bang session gia."""

import pytest
import requests

import lt_scan_vietcap as vc


class _TraLoi:
    def __init__(self, ma, json=None):
        self.status_code, self._json = ma, json

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class _SessionGia:
    def __init__(self, kich_ban):
        self.kich_ban = list(kich_ban)
        self.so_goi = 0

    def request(self, method, url, timeout=None, **kw):
        assert timeout == (vc.KET_NOI_TOI_DA, vc.DOC_TOI_DA)
        self.so_goi += 1
        x = self.kich_ban.pop(0)
        if isinstance(x, Exception):
            raise x
        return x


@pytest.fixture
def gia(monkeypatch):
    ngu = []
    monkeypatch.setattr(vc.time, "sleep", ngu.append)
    monkeypatch.setattr(vc, "PHANH", vc._Phanh())
    monkeypatch.setattr(vc, "PHANH_VND", vc._Phanh())
    monkeypatch.setattr(vc, "VIETCAP_NGAT", vc.threading.Event())

    def dat(kich_ban):
        s = _SessionGia(kich_ban)
        monkeypatch.setattr(vc, "_session", lambda: s)
        return s
    dat.ngu = ngu
    return dat


def test_bi_chan_roi_thong(gia):
    s = gia([_TraLoi(418), requests.exceptions.ReadTimeout(), _TraLoi(200, [{"ok": 1}])])
    assert vc._goi("POST", vc.PX_URL, json={}) == [{"ok": 1}]
    assert s.so_goi == 3
    assert vc.PHANH.so_chan == 2
    assert vc.PHANH.chan_lien == 0                 # thong -> reset chuoi chan
    assert max(gia.ngu) >= 5                       # co nghi chung sau khi bi chan


def test_chan_mai_thi_raise(gia):
    gia([_TraLoi(418)] * vc.LAN_THU)
    with pytest.raises(requests.HTTPError):
        vc._goi("GET", vc.LIST_URL)
    assert vc.PHANH.so_chan == vc.LAN_THU


def test_loi_khac_khong_thu_lai(gia):
    s = gia([_TraLoi(404)])
    with pytest.raises(requests.HTTPError):
        vc._goi("GET", vc.LIST_URL)
    assert s.so_goi == 1


BAR = [["2026-10-23", 1, 1, 1, 1, 1]] * 30


def test_vietcap_loi_thi_lay_vnd(gia, monkeypatch):
    def tai_bar(ma, to_ts):
        if ma == "BBB":
            raise requests.HTTPError("HTTP 418")
        return BAR
    monkeypatch.setattr(vc, "tai_bar", tai_bar)
    monkeypatch.setattr(vc, "tai_bar_vnd", lambda ma, to_ts: BAR)
    bars, loi, mat, nguon = vc.quet(["AAA", "BBB"], 0, "2026-10-23", luong=2)
    assert sorted(bars) == ["AAA", "BBB"] and mat == [] and loi == []
    assert nguon == {"AAA": "vietcap", "BBB": "vnd"}
    assert not vc.VIETCAP_NGAT.is_set()            # mot lan loi le, chua ngat


def test_quet_vet_khi_tat_du_phong(gia, monkeypatch):
    lan = {}

    def tai_bar(ma, to_ts):
        lan[ma] = lan.get(ma, 0) + 1
        if ma == "BBB" and lan[ma] == 1:
            raise requests.HTTPError("HTTP 418")
        return BAR

    def khong_duoc_goi(ma, to_ts):
        raise AssertionError("tat du phong ma van goi VNDirect")
    monkeypatch.setattr(vc, "tai_bar", tai_bar)
    monkeypatch.setattr(vc, "tai_bar_vnd", khong_duoc_goi)
    bars, loi, mat, nguon = vc.quet(["AAA", "BBB"], 0, "2026-10-23", luong=2, du_phong=False)
    assert sorted(bars) == ["AAA", "BBB"] and mat == [] and lan["BBB"] == 2
    assert set(nguon.values()) == {"vietcap"}


def test_chan_lien_tiep_thi_ngat_vietcap(gia, monkeypatch):
    goi_vc = []

    def tai_bar(ma, to_ts):
        goi_vc.append(ma)
        for _ in range(vc.NGAT_SAU):
            vc.PHANH.bi_chan()
        raise requests.HTTPError("HTTP 418")
    monkeypatch.setattr(vc, "tai_bar", tai_bar)
    monkeypatch.setattr(vc, "tai_bar_vnd", lambda ma, to_ts: BAR)
    bars, _, mat, nguon = vc.quet(["AAA", "BBB", "CCC"], 0, "2026-10-23", luong=1)
    assert vc.VIETCAP_NGAT.is_set()
    assert goi_vc == ["AAA"]                       # sau khi ngat khong goi Vietcap nua
    assert sorted(bars) == ["AAA", "BBB", "CCC"] and mat == []
    assert set(nguon.values()) == {"vnd"}


def test_doc_vnd_nhan_nghin_bo_kl_0():
    t = int(vc.datetime(2026, 10, 26, 7).timestamp())
    d = {"s": "ok", "t": [t, t + 86400, t + 2 * 86400], "o": [21.3, 21.4, 21.5],
         "h": [21.5, 21.6, 21.7], "l": [21.1, 21.2, 21.3], "c": [21.35, 21.4, 21.45],
         "v": [8398900, 0, 6732700]}
    b = vc.doc_vnd(d)
    assert [x[0] for x in b] == ["2026-10-26", "2026-10-28"]
    assert b[0][1:] == [21300.0, 21500.0, 21100.0, 21350.0, 8398900.0]
    assert vc.doc_vnd({"s": "no_data"}) is None


def test_vnd_khong_lay_vnindex():
    with pytest.raises(ValueError):
        vc.tai_bar_vnd("VNINDEX", 0)


# ------------------------------------------------------------------ hai tang
def _dong(tov):
    """Mot dong ban quet du 15 truong; chi tov_ty (cot 8) quan trong cho chon_ma."""
    return [10.0, 0, 0, 0, 0, 10, 10, 0.02, tov, [], 0, 0, [0, 0, 0], [], []]


def test_chon_ma_hai_tang():
    ngay = "2026-10-30"
    nhom = vc.nhom_cua_ngay(ngay)
    ma = [f"M{i:03d}" for i in range(200)]
    trung = next(m for m in ma if vc.nhom_xoay(m) == nhom)
    lech = [m for m in ma if vc.nhom_xoay(m) != nhom]
    long, thuong, giu, cu, moi = lech[0], lech[1], lech[2], lech[3], lech[4]
    goc = {m: _dong(0.2) for m in ma if m != moi}
    goc[long] = _dong(5.0)
    goc["VNINDEX"] = _dong(9999)
    goc["_meta"] = {"ngay_du_lieu": "2026-10-22"}
    goc["_mang_sang"] = {cu: "2026-10-01"}          # dong mang sang qua 14 ngay -> bat buoc tai
    tai, ms, tang1, info = vc.chon_ma(set(ma), goc, {giu}, ngay)
    assert {long, giu} <= tang1 and thuong not in tang1
    assert trung in tai and cu in tai and long in tai and giu in tai
    assert thuong not in tai and ms[thuong] == "2026-10-22"
    assert moi not in tai and moi not in ms         # chua co dong, chua toi nhom -> doi luot
    assert "VNINDEX" not in tai and "VNINDEX" not in ms
    assert info["qua_han"] == 1
    # Thu 2..Thu 6 (5 ngay lich lien tiep) phu du 5 nhom.
    assert {vc.nhom_cua_ngay(f"2026-11-0{d}") for d in range(2, 7)} == set(range(vc.SO_NHOM_XOAY))


def _bars(ngay_ds, gia0=100.0):
    return [[d, gia0 + i, gia0 + i, gia0 + i, gia0 + i, 1000.0] for i, d in enumerate(ngay_ds)]


def test_dung_ban_quet_nhieu_phien_va_mang_sang():
    ngay = [f"2026-09-{d:02d}" for d in range(1, 31)] + ["2026-10-01", "2026-10-02"]
    bars = {"VNINDEX": _bars(ngay), "AAA": _bars(ngay), "BBB": _bars(ngay[:-1])}
    goc = {"CCC": _dong(0.1), "_meta": {"ngay_du_lieu": "2026-09-30"},
           "_san": {"CCC": "UPCOM"}, "_icb": {"CCC": "1300"}}
    san_icb = {"AAA": {"san": "HSX", "icb": "8300"}, "BBB": {"san": "HNX", "icb": "8300"}}
    nguon = {"AAA": "vietcap", "BBB": "vnd", "VNINDEX": "vietcap"}
    meta = {"che_do_quet": "hai_tang", "loi": []}
    p1 = vc.dung_ban_quet(bars, "2026-10-01", san_icb, goc, {"CCC": "2026-09-30"}, nguon, meta)
    p2 = vc.dung_ban_quet(bars, "2026-10-02", san_icb, goc, {"CCC": "2026-09-30"}, nguon, meta)
    assert p1["_meta"]["ngay_du_lieu"] == "2026-10-01" and p1["AAA"][0] == 130.0
    assert p2["_meta"]["ngay_du_lieu"] == "2026-10-02" and p2["AAA"][0] == 131.0
    assert p1["_meta"]["bar_cuoi_lech_ngay"] == [] and p2["_meta"]["bar_cuoi_lech_ngay"] == ["BBB"]
    assert p2["CCC"] == goc["CCC"] and p2["_mang_sang"] == {"CCC": "2026-09-30"}
    assert p2["_san"]["CCC"] == "UPCOM" and p2["_san"]["AAA"] == "HSX"
    assert p2["_meta"]["nguon_vnd"] == ["BBB"]
    assert p2["_vnindex"]["t"][-1] == "2026-10-02" and p1["_vnindex"]["t"][-1] == "2026-10-01"
