import json
from ranking import pct_rank as rank_pct

d = {}
for p in ['part1', 'part2']:
    with open(f'data/scan_weekly_20260824_{p}.json', encoding='utf-8') as f:
        d.update(json.load(f))
print(len(d), 'symbols total')

vnindex = d.pop('VNINDEX')
FIELDS = ['close', 'r5', 'r10', 'r20', 'volRatio', 'distHigh20', 'rsi14', 'atr_pct', 'turnover_ty20d']

universe = {}
for sym, m in d.items():
    close, r5, r10, r20, volr, dist, rsi, atr, to = m
    if to is None or to < 10:
        continue
    if atr is None or atr > 0.08:
        continue
    universe[sym] = m

print(len(universe), 'sau loc thanh khoan/ATR')


syms = list(universe.keys())
r5v = [universe[s][1] for s in syms]
r10v = [universe[s][2] for s in syms]
volv = [universe[s][4] for s in syms]
distv = [universe[s][5] for s in syms]

pr5 = rank_pct(r5v)
pr10 = rank_pct(r10v)
pvol = rank_pct(volv)
pdist = rank_pct(distv)

scores = []
for i, s in enumerate(syms):
    sc = 0.40 * pr5[i] + 0.25 * pr10[i] + 0.20 * pvol[i] + 0.15 * pdist[i]
    scores.append((sc, s))
scores.sort(reverse=True)

print(f"\nVNINDEX tuan qua: close {vnindex[0]}  r5 {vnindex[1]*100:.2f}%  r10 {vnindex[2]*100:.2f}%  "
      f"r20 {vnindex[3]*100:.2f}%  volRatio {vnindex[4]}  distHigh20 {vnindex[5]*100:.2f}%  RSI {vnindex[6]}")
print("\nTop 15 theo diem momentum tuan "
      "(0.40*r5 + 0.25*r10 + 0.20*volRatio + 0.15*distHigh20, tat ca theo phan vi):")
print(f"{'#':<3}{'Ma':<6}{'Score':<7}{'Gia':<9}{'r5%':<8}{'r10%':<8}{'volR':<7}{'distH20%':<10}"
      f"{'RSI':<6}{'ATR%':<7}{'TO(ty)':<8}")
for i, (sc, s) in enumerate(scores[:15]):
    m = universe[s]
    print(f"{i+1:<3}{s:<6}{sc:<7.3f}{m[0]:<9}{m[1]*100:<8.2f}{m[2]*100:<8.2f}{m[4]:<7.2f}"
          f"{m[5]*100:<10.2f}{m[6]:<6.1f}{m[7]*100:<7.2f}{m[8]:<8.1f}")

json.dump(
    {'_note': 'weekly momentum scan, tinh den 2026-08-24', 'vnindex': dict(zip(FIELDS, vnindex)),
     'universe': {s: dict(zip(FIELDS, universe[s])) for s in syms}},
    open('data/scan_weekly_20260824.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
