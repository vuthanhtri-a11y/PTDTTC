"""bieu_do.py — Bieu do dung chung nhieu tab (VN-Index co to nen che do)."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard import ui
from dashboard.thi_truong import doan_che_do


def vnindex(vn, so_phien=250, khoi_luong=True, cao=460):
    """VN-Index + MA50/MA200 + nguong vao Giam, nen to theo che do, danh dau phien phan phoi."""
    m = ui.mau()
    v = vn.tail(so_phien)
    if khoi_luong:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2],
                            vertical_spacing=0.03)
    else:
        fig = go.Figure()
    kw = dict(row=1, col=1) if khoi_luong else {}
    fig.add_trace(ui.go_line(v["ngay"], v["c"], "VN-Index", m["s1"]), **kw)
    # Them nen SAU khi co trace: add_vrect bo qua subplot rong.
    for tu, den, st_ in doan_che_do(v):
        fig.add_vrect(x0=tu, x1=den, fillcolor=ui.CHE_DO_MAU[st_], opacity=0.13,
                      line_width=0, layer="below", **kw)
    fig.add_trace(ui.go_line(v["ngay"], v["ma50"], "MA50", m["s2"], 1.5), **kw)
    fig.add_trace(ui.go_line(v["ngay"], v["ma200"], "MA200 (ra Giảm khi đóng cửa trên)",
                             m["s3"], 1.5), **kw)
    fig.add_trace(go.Scatter(x=v["ngay"], y=v["nguong_vao_giam"], name="0,97 × MA200 (vào Giảm)",
                             mode="lines", line=dict(color=m["chu_3"], width=1, dash="dot")), **kw)
    pp = v[v["phan_phoi_cua_so"]]
    fig.add_trace(go.Scatter(x=pp["ngay"], y=pp["c"], name=f"Phiên phân phối trong 25 phiên ({len(pp)})",
                             mode="markers",
                             marker=dict(symbol="triangle-down", size=8, color=m["giam"],
                                         line=dict(color=m["be_mat"], width=1))), **kw)
    # Chu giai cho nen to (khong co du lieu, chi de legend doc duoc mau).
    for st_ in ("TANG", "DIEU_CHINH", "GIAM"):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Nền: {ui.CHE_DO_TEN[st_]}",
                                 marker=dict(symbol="square", size=12, color=ui.CHE_DO_MAU[st_],
                                             opacity=0.35), hoverinfo="skip"), **kw)
    if khoi_luong:
        fig.add_trace(go.Bar(x=v["ngay"], y=v["v"], name="KL khớp", marker_color=m["chu_3"],
                             showlegend=False), row=2, col=1)
    ui.khung(fig, cao=cao)
    fig.update_yaxes(tickformat=",.0f", side="right")     # truc gia ben phai kieu terminal
    return fig


def duong(df, cot_mau, cao=300, dinh_dang=None, nhan_cuoi=True, chu_y=None):
    """Nhieu duong tren MOT truc; cot_mau = [(cot, ten, mau)]. Nhan truc tiep o diem cuoi.

    Nhan cuoi duoc day cach nhau toi thieu ~7% bien do truc tung de khong chong chu.
    """
    m = ui.mau()
    dinh_dang = dinh_dang or (lambda x: ui.so(x, 1))
    fig = go.Figure()
    nhan = []
    for cot, ten, mau_ in cot_mau:
        s = df[cot].dropna()
        fig.add_trace(ui.go_line(s.index, s.values, ten, mau_))
        if nhan_cuoi and len(s):
            nhan.append([s.iloc[-1], s.index[-1], f"{ten} {dinh_dang(s.iloc[-1])}"])
    if nhan:
        vals = df[[c for c, _, _ in cot_mau]].to_numpy(dtype=float)
        bien = float(pd.Series(vals.ravel()).max() - pd.Series(vals.ravel()).min()) or 1.0
        nhan.sort(key=lambda x: x[0])
        y_hien = []
        for y, _, _ in nhan:
            y_hien.append(y if not y_hien else max(y, y_hien[-1] + 0.07 * bien))
        for (y, x, txt), yh in zip(nhan, y_hien):
            fig.add_annotation(x=x, y=yh, text=txt, showarrow=False, xanchor="left", xshift=6,
                               font=dict(size=11, color=m["chu_2"]))
    ui.khung(fig, cao=cao, chu_y=chu_y)
    if nhan_cuoi:
        fig.update_layout(margin=dict(r=150))
        # Nhan cuoi nam o le phai: chot truc x vao du lieu, khong de autorange keo dai theo chu.
        x = df.index[df[[c for c, _, _ in cot_mau]].notna().any(axis=1)]
        if len(x):
            fig.update_xaxes(range=[x[0], x[-1]])
    return fig


def heatmap(ma_tran, chu_y=None, phan_ky=True, cao=None, dinh_dang=None):
    """Heatmap co so ghi trong o (khong de mau mot minh mang nghia)."""
    m = ui.mau()
    z = ma_tran.to_numpy(dtype=float)
    dinh_dang = dinh_dang or (lambda x: ui.pt(x, 1))
    txt = [[dinh_dang(x) if pd.notna(x) else "" for x in row] for row in z]
    if phan_ky:
        lim = float(pd.Series(z.ravel()).abs().quantile(0.95) or 0.01)
        cs = dict(colorscale=ui.thang_phan_ky(), zmid=0, zmin=-lim, zmax=lim)
    else:
        cs = dict(colorscale=[[0, m["lien_tuc"][0]], [1, m["lien_tuc"][1]]])
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in ma_tran.columns], y=list(ma_tran.index), text=txt,
        texttemplate="%{text}", textfont=dict(size=11, color=m["chu"]), xgap=2, ygap=2,
        hovertemplate="%{y} · %{x}: %{text}<extra></extra>", showscale=False, **cs))
    ui.khung(fig, cao=cao or max(260, 26 * len(ma_tran) + 60), chu_y=chu_y, legend=False)
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_layout(hovermode="closest")
    return fig
