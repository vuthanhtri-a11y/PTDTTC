"""
ui.py — Giao dien "Medici Terminal": khung Bloomberg terminal, mau chu dao cua bao cao
Medici (do tu `medici - mid term report.pdf`, 07/10/2026).

Token ba lop: NGUYEN_THUY (mau goc Medici) -> M (vai tro ngu nghia) -> CSS / Plotly.
  #390A5B tim dam (bia, trang chuong)   #682996 tim chinh (logo, tieu de bang)
  #BB99FF tim nhat (diem nhan)          #FCF9EA kem (chu tren nen tim)
  #E4D4F2 / #F7F3FF lavender (to dong)  Francois One (tieu de), so lieu IBM Plex Mono.
Terminal luon nen toi (nhu Bloomberg); khong co bien the sang.

Mau bieu do da chay validate_palette.js (ky nang dataviz) tren nen #110A1A:
s1 #9D7BEA · s2 #C98500 · s3 #199E70 — dat moi kiem tra, ke ca all-pairs. Mau trang
thai (tang/giam, che do) luon di kem dau +/- hoac nhan chu, khong de mau mang nghia mot minh.
"""

import html
import math

import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------ so
def so(x, d=0, dau=False):
    """1737.71 -> '1.737,71'. None/NaN -> '—'."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if round(x, d) == 0:                    # 0 khong mang dau: "0,00%", khong "+0,00%"/"-0,00%"
        x, dau = 0.0, False
    s = f"{x:+,.{d}f}" if dau else f"{x:,.{d}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def pt(x, d=1, dau=True):
    """0.0329 -> '+3,3%'."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return so(x * 100, d, dau) + "%"


def ngay_vn(iso):
    """'2026-10-02' -> '02/10/2026'."""
    if not iso:
        return "—"
    s = str(iso)[:10]
    return f"{s[8:10]}/{s[5:7]}/{s[:4]}"


def bang(df, so_cot=None, pt_cot=None, pt_khong_dau=None, ngay_cot=None):
    """Styler dinh dang so kieu VN; gia tri goc giu nguyen de sap xep dung."""
    fmt = {}
    for c, d in (so_cot or {}).items():
        fmt[c] = lambda x, d=d: so(x, d)
    for c, d in (pt_cot or {}).items():
        fmt[c] = lambda x, d=d: pt(x, d)
    for c, d in (pt_khong_dau or {}).items():
        fmt[c] = lambda x, d=d: pt(x, d, dau=False)
    for c in ngay_cot or []:
        fmt[c] = ngay_vn
    fmt = {c: f for c, f in fmt.items() if c in df.columns}
    return df.style.format(fmt, na_rep="—")


# ------------------------------------------------------------------ token
NGUYEN_THUY = {
    "tim_950": "#0C0613",   # thanh ben
    "tim_900": "#110A1A",   # nen terminal — tim gan den, keo tu #390A5B
    "tim_850": "#170E23",   # panel
    "tim_800": "#20142F",   # dai tieu de panel, header bang
    "tim_750": "#2A1C3B",   # luoi
    "tim_700": "#3B2A50",   # vien
    "medici_dam": "#390A5B",
    "medici": "#682996",
    "medici_vua": "#8B5CD6",  # mau tuong tac: 4,25:1 tren nen, chu trang 4,57:1
    "medici_nhat": "#BB99FF",
    "lavender": "#E4D4F2",
    "kem": "#FCF9EA",
}
N = NGUYEN_THUY
M = {
    "be_mat": N["tim_900"], "panel": N["tim_850"], "panel_2": N["tim_800"],
    "chu": N["kem"], "chu_2": "#C9B8DE", "chu_3": "#9A88B2",
    "nhan": N["medici_nhat"],                       # vai tro "amber" cua Bloomberg: nhan, tieu de
    "luoi": N["tim_750"], "truc": N["tim_700"],
    "s1": "#9D7BEA", "s2": "#C98500", "s3": "#199E70",
    "tang": "#41D17F", "giam": "#FF6B6B",            # chu: 9,8:1 / 7,0:1 tren nen
    "phan_ky": ["#B03A3A", "#2A1F36", "#2E5FB8"],    # giam <-> 0 <-> tang; chu kem >= 5,6:1
    "lien_tuc": ["#24163A", "#7E52C4"],              # gan 0 lui ve nen; chu kem >= 5,1:1
}
# Trang thai co dinh: tot / canh bao / nghiem trong — luon kem dau va chu.
CHE_DO_MAU = {"TANG": "#0ca30c", "DIEU_CHINH": "#fab219", "GIAM": "#d03b3b"}
CHE_DO_TEN = {"TANG": "TĂNG", "DIEU_CHINH": "ĐIỀU CHỈNH", "GIAM": "GIẢM", None: "KHÔNG XÁC ĐỊNH"}
CHE_DO_DAU = {"TANG": "▲", "DIEU_CHINH": "◆", "GIAM": "▼", None: "?"}
NHIP = {"HANG NGAY": "hằng ngày", "KY SOAT": "kỳ soát"}
PHONG_SO = '"IBM Plex Mono", ui-monospace, Consolas, monospace'
PHONG_TIEU_DE = '"Francois One", "Arial Narrow", sans-serif'


def mau():
    return M


def mau_delta(x):
    if x is None or (isinstance(x, float) and math.isnan(x)) or x == 0:
        return M["chu_2"]
    return M["tang"] if x > 0 else M["giam"]


def thang_phan_ky():
    d, g, t = M["phan_ky"]
    return [[0, d], [0.5, g], [1, t]]


# ------------------------------------------------------------------ bieu do
def khung(fig, cao=360, chu_y=None, legend=True):
    # Co tieu de: tieu de o dinh khung, legend ngay duoi, roi moi toi vung ve.
    fig.update_layout(
        height=cao, margin=dict(l=8, r=8, t=(78 if legend else 40) if chu_y else 28, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=PHONG_SO, color=M["chu_2"], size=11),
        separators=",.", hovermode="x unified", showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font=dict(color=M["chu_2"], size=11)),
        hoverlabel=dict(font=dict(family=PHONG_SO, color=M["chu"], size=12),
                        bgcolor=M["panel_2"], bordercolor=M["nhan"]),
    )
    if chu_y:
        fig.update_layout(title=dict(text=chu_y.upper(),
                                     font=dict(family=PHONG_TIEU_DE, size=14, color=M["nhan"]),
                                     x=0, xanchor="left", y=1, yref="container", yanchor="top",
                                     pad=dict(t=6)))
    fig.update_xaxes(showgrid=False, linecolor=M["truc"], tickcolor=M["truc"],
                     tickfont=dict(color=M["chu_3"]), automargin=True)
    fig.update_yaxes(gridcolor=M["luoi"], zeroline=False, linecolor=M["truc"],
                     tickfont=dict(color=M["chu_3"]), automargin=True)
    return fig


def ve(fig, key=None):
    st.plotly_chart(fig, width="stretch", theme=None, key=key,
                    config={"displaylogo": False, "locale": "vi"})


# ------------------------------------------------------------------ CSS
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Francois+One&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
:root{{--nen:{M["be_mat"]};--panel:{M["panel"]};--panel2:{M["panel_2"]};--luoi:{M["luoi"]};
  --vien:{M["truc"]};--chu:{M["chu"]};--chu2:{M["chu_2"]};--chu3:{M["chu_3"]};--nhan:{M["nhan"]};
  --medici:{N["medici"]};--medici-dam:{N["medici_dam"]};--tang:{M["tang"]};--giam:{M["giam"]};
  --so:{PHONG_SO};--td:{PHONG_TIEU_DE}}}
html,body,[data-testid="stAppViewContainer"]{{font-variant-numeric:tabular-nums}}
[data-testid="stHeader"]{{background:transparent}}
[data-testid="stDecoration"]{{background:linear-gradient(90deg,var(--medici-dam),var(--medici),var(--nhan))}}
.block-container{{padding-top:2.6rem;max-width:100%}}
/* tieu de panel: dai chu in hoa kieu terminal */
h5,[data-testid="stHeading"] h5{{font-family:var(--td)!important;font-weight:400!important;
  text-transform:uppercase;letter-spacing:.06em;color:var(--nhan)!important;font-size:15px!important;
  border-bottom:1px solid var(--vien);padding:2px 0 4px!important;margin:14px 0 8px!important}}
h3,h4{{font-family:var(--td)!important;font-weight:400!important;letter-spacing:.03em}}
/* thanh lenh tren cung */
.tm-bar{{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;background:var(--medici-dam);
  border:1px solid var(--medici);padding:6px 10px;margin:0 0 2px}}
.tm-logo{{font-family:var(--td);font-size:20px;letter-spacing:.12em;color:var(--chu)}}
.tm-logo b{{color:var(--nhan);font-weight:400}}
.tm-cmd{{flex:1;min-width:220px;font-family:var(--so);font-size:13px;color:var(--chu);
  background:var(--nen);border:1px solid var(--medici);padding:3px 8px}}
.tm-cmd .go{{background:var(--medici);color:var(--chu);padding:0 6px;margin-left:6px;font-weight:600}}
.tm-cmd .nhay{{animation:nhay 1s steps(1) infinite;color:var(--nhan)}}
@keyframes nhay{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.tm-cmd .nhay{{animation:none}}}}
.tm-phai{{font-family:var(--so);font-size:12px;color:var(--chu2);display:flex;gap:10px;align-items:center}}
.tm-bang{{display:flex;flex-wrap:wrap;gap:0;font-family:var(--so);font-size:12px;
  background:var(--panel);border:1px solid var(--vien);border-top:0;margin:0 0 10px}}
.tm-bang span{{padding:3px 10px;border-right:1px solid var(--luoi);white-space:nowrap}}
.tm-bang .ma{{color:var(--nhan);font-weight:600;margin-right:6px}}
.tm-bang .gt{{color:var(--chu)}}
/* phim chuc nang = tab (Streamlit 1.65: div[role=tab] trong div[role=tablist]) */
[role="tablist"]{{gap:2px!important;border-bottom:1px solid var(--vien);flex-wrap:wrap}}
[role="tablist"] .react-aria-SelectionIndicator{{display:none!important}}
[data-testid="stTab"]{{background:var(--panel2)!important;border:1px solid var(--vien)!important;
  border-bottom:0!important;padding:4px 12px!important;margin:0!important;border-radius:0!important}}
[data-testid="stTab"] p{{font-family:var(--so)!important;font-size:12px!important;text-transform:uppercase;
  letter-spacing:.04em;color:var(--chu2)!important}}
[data-testid="stTab"][aria-selected="true"]{{background:var(--medici)!important;border-color:var(--nhan)!important}}
[data-testid="stTab"][aria-selected="true"] p{{color:var(--chu)!important;font-weight:600}}
[data-testid="stTab"]:hover p{{color:var(--chu)!important}}
/* o so lieu */
.o-wrap{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:2px;margin:4px 0 12px}}
.o{{background:var(--panel);padding:7px 10px;border:1px solid var(--luoi);border-left:2px solid var(--medici)}}
.o .nhan{{font-family:var(--so);font-size:11px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--nhan);margin-bottom:2px}}
.o .gt{{font-family:var(--so);font-size:21px;font-weight:600;line-height:1.25;color:var(--chu)}}
.o .phu{{font-family:var(--so);font-size:11.5px;margin-top:2px;color:var(--chu2)}}
.the-che-do{{display:inline-block;padding:1px 8px;font-family:var(--so);font-weight:700;font-size:12px;
  letter-spacing:.05em;vertical-align:middle}}
.canh-bao{{border-left:3px solid #fab219;padding:5px 10px;margin:3px 0;background:rgba(250,178,25,.08);
  font-family:var(--so);font-size:12.5px;color:var(--chu)}}
.canh-bao.nang{{border-left-color:#d03b3b;background:rgba(208,59,59,.12)}}
.nhan-kp{{border:1px dashed var(--nhan);padding:6px 10px;font-family:var(--so);font-size:12.5px;margin-bottom:8px}}
[data-testid="stCaptionContainer"]{{font-family:var(--so);font-size:11.5px;color:var(--chu3)}}
[data-testid="stSidebar"] h2{{font-family:var(--td);font-weight:400;letter-spacing:.1em}}
</style>
"""


def nap_css():
    st.markdown(CSS, unsafe_allow_html=True)


def thanh_lenh(lenh, phai_html):
    """Thanh lenh kieu terminal: logo MEDICI, dong lenh <GO>, trang thai ben phai."""
    st.markdown(
        '<div class="tm-bar"><div class="tm-logo">MEDICI <b>TERMINAL</b></div>'
        f'<div class="tm-cmd">{html.escape(lenh)} <span class="go">GO</span>'
        '<span class="nhay">▌</span></div>'
        f'<div class="tm-phai">{phai_html}</div></div>', unsafe_allow_html=True)


def bang_gia(cac_ma):
    """Dai bao gia duoi thanh lenh: [(ma, gia tri, thay doi | None)]."""
    phan = []
    for ma, gt, r in cac_ma:
        bd = "" if r is None else (f' <span style="color:{mau_delta(r)}">'
                                   f'{"▲" if r > 0 else ("▼" if r < 0 else "■")}{pt(abs(r), 2, dau=False)}</span>')
        phan.append(f'<span><span class="ma">{html.escape(ma)}</span><span class="gt">{gt}</span>{bd}</span>')
    st.markdown('<div class="tm-bang">' + "".join(phan) + "</div>", unsafe_allow_html=True)


def o_so(cac_o):
    """cac_o: [(nhan, gia tri, dong phu, mau dong phu | None)]."""
    phan = []
    for nhan, gt, phu, mau_phu in cac_o:
        style = f' style="color:{mau_phu}"' if mau_phu else ""
        phan.append(f'<div class="o"><div class="nhan">{html.escape(nhan)}</div>'
                    f'<div class="gt">{gt}</div>'
                    + (f'<div class="phu"{style}>{phu}</div>' if phu else "") + "</div>")
    st.markdown('<div class="o-wrap">' + "".join(phan) + "</div>", unsafe_allow_html=True)


def the_che_do(st_):
    chu = "#ffffff" if st_ == "GIAM" else "#0b0b0b"     # do dam: chu trang moi du tuong phan
    return (f'<span class="the-che-do" style="background:{CHE_DO_MAU.get(st_, "#9A88B2")};'
            f'color:{chu}">{CHE_DO_DAU[st_]} {CHE_DO_TEN[st_]}</span>')


def canh_bao(txt, nang=False):
    st.markdown(f'<div class="canh-bao{" nang" if nang else ""}">{txt}</div>',
                unsafe_allow_html=True)


def to_mau_delta(cot):
    """Styler: to chu tang/giam cho cac cot loi suat (kem dau +/- trong dinh dang)."""
    def f(v):
        if v is None or (isinstance(v, float) and math.isnan(v)) or v == 0:
            return ""
        return f"color:{M['tang'] if v > 0 else M['giam']}"
    return [f(v) for v in cot]


def them_mau_delta(sty, cac_cot):
    cac_cot = [c for c in cac_cot if c in sty.data.columns]
    if cac_cot:
        sty = sty.apply(to_mau_delta, subset=cac_cot)
    return sty


def go_line(x, y, ten, mau_, rong=2, mode="lines", **kw):
    return go.Scatter(x=x, y=y, name=ten, mode=mode, line=dict(color=mau_, width=rong),
                      marker=dict(size=8, color=mau_), **kw)
