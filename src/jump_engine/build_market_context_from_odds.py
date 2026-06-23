"""Small helper to convert 1X2 decimal odds into no-vig probabilities.

Input CSV columns:
    match,home_team,away_team,home_odds,draw_odds,away_odds,total_line(optional)
Output:
    data/derived/market_1x2_fair.csv
"""
from __future__ import annotations
import argparse, csv
from pathlib import Path


def f(x): return float(str(x).strip())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', default='data/derived/market_1x2_fair.csv')
    args=ap.parse_args()
    rows=[]
    with Path(args.input).open('r', newline='', encoding='utf-8-sig') as fp:
        for r in csv.DictReader(fp):
            inv_h, inv_d, inv_a = 1/f(r['home_odds']), 1/f(r['draw_odds']), 1/f(r['away_odds'])
            z = inv_h + inv_d + inv_a
            rows.append({
                'match': r.get('match',''), 'home_team': r.get('home_team',''), 'away_team': r.get('away_team',''),
                'home_fair': round(inv_h/z, 4), 'draw_fair': round(inv_d/z, 4), 'away_fair': round(inv_a/z, 4),
                'overround': round(z-1, 4), 'total_line': r.get('total_line','')
            })
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as fp:
        w=csv.DictWriter(fp, fieldnames=['match','home_team','away_team','home_fair','draw_fair','away_fair','overround','total_line'])
        w.writeheader(); w.writerows(rows)
    print(f'Wrote {out} ({len(rows)} rows)')

if __name__=='__main__': main()
