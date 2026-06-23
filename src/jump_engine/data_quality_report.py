from __future__ import annotations
import argparse, csv
from pathlib import Path


def read(path):
    with Path(path).open('r', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='data')
    args = ap.parse_args()
    d = Path(args.data_dir)
    pool = read(d/'player_pool.csv')
    att = {r['player']: r for r in read(d/'player_attacking_stats.csv')} if (d/'player_attacking_stats.csv').exists() else {}
    dis = {r['player']: r for r in read(d/'player_defensive_discipline.csv')} if (d/'player_defensive_discipline.csv').exists() else {}
    rows = []
    for p in pool:
        name = p['player']
        a, x = att.get(name, {}), dis.get(name, {})
        minutes = p.get('expected_minutes') or 'auto'
        red = []
        if name not in att: red.append('missing attacking')
        if name not in dis: red.append('missing discipline')
        if a and float(a.get('shots90') or 0) == 0 and p.get('position') != 'GK': red.append('zero shots90')
        if x and float(x.get('fouls_committed90') or 0) == 0 and p.get('position') != 'GK': red.append('zero fouls90')
        rows.append({'player': name, 'team': p.get('team',''), 'club': p.get('club',''), 'minutes': minutes, 'flags': '; '.join(red)})
    out = d/'derived'/'data_quality_report.csv'
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['player','team','club','minutes','flags'])
        w.writeheader(); w.writerows(rows)
    print(f'Wrote {out}')
    print(f'Flagged rows: {sum(bool(r["flags"]) for r in rows)} / {len(rows)}')

if __name__ == '__main__': main()
