#!/usr/bin/env python3
"""Conservative descriptive statistics for two resident SMS archives from one building."""
from __future__ import annotations
from pathlib import Path
import argparse,csv
from datetime import date,timedelta
from decimal import Decimal,localcontext,ROUND_HALF_UP
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]; GROUPS=ROOT/'data'/'derived'/'notification_groups.csv'
def ftxt(v): return str(v.numerator) if v.denominator==1 else f'{v.numerator}/{v.denominator}'
def exact_decimal(v):
 d=v.denominator;a=b=0
 while d%2==0:d//=2;a+=1
 while d%5==0:d//=5;b+=1
 if d!=1:return None
 p=max(a,b);x=v*10**p; assert x.denominator==1
 if p==0:return str(x.numerator)
 s='-' if x.numerator<0 else '';q=str(abs(x.numerator)).rjust(p+1,'0');return f'{s}{q[:-p]}.{q[-p:]}'
def rounded(v,p):
 with localcontext() as c:
  c.prec=max(50,p+30);d=Decimal(v.numerator)/Decimal(v.denominator);return format(d.quantize(Decimal(1).scaleb(-p),rounding=ROUND_HALF_UP),'f')
def display(v,p=3):
 e=exact_decimal(v)
 return ftxt(v) if v.denominator==1 else (f'{ftxt(v)} = {e}' if e is not None else f'{ftxt(v)} (decimal rounded to {p} dp: {rounded(v,p)})')
def load_groups():
 out=[]
 with GROUPS.open(encoding='utf-8') as f:
  for r in csv.DictReader(f):r['anchor_date']=date.fromisoformat(r['anchor_date']);out.append(r)
 return out
def source_in(r,s): return s in r['evidence_sites'].split(';')
def site_in(r,s): return source_in(r,s)  # backwards-compatible helper name
def fully_contained_window_max(rows,days,span_start,span_end):
 if not rows or (span_end-span_start).days+1<days:return None
 best=None;start=span_start;last=span_end-timedelta(days=days-1)
 while start<=last:
  end=start+timedelta(days=days-1);sel=sorted((r for r in rows if start<=r['anchor_date']<=end),key=lambda r:(r['anchor_date'],r['group_id']));cand=(len(sel),start,end,sel)
  if best is None or cand[0]>best[0]:best=cand
  start+=timedelta(days=1)
 return best
def median_int(vals):
 o=sorted(vals);m=len(o)//2;return Fraction(o[m],1) if len(o)%2 else Fraction(o[m-1]+o[m],2)
def gap_stats(rows):
 d=sorted(r['anchor_date'] for r in rows);g=[(b-a).days for a,b in zip(d,d[1:])]
 return None if not g else (Fraction(sum(g),len(g)),median_int(g),min(g),max(g))
def render():
 rows=load_groups(); dates=sorted(r['anchor_date'] for r in rows);rs,re=min(dates),max(dates);span=(re-rs).days+1
 em=[r for r in rows if r['category']=='emergency'];sw=[r for r in rows if r['category']=='network_switching'];pl=[r for r in rows if r['category']=='planned']
 out=[];E=out.append
 E(f'Source-record anchor span: {rs} to {re} inclusive = {span} calendar days');E('IMPORTANT: retrospective transcript span, not a proven complete observation window.')
 E('SITE_A and SITE_B are legacy source IDs for two residents of the same Orkhevi building, not two geographic sites.')
 E(f'Emergency notification groups keyed by restoration-ETA date: {len(em)}');E(f'Network-switching notification groups keyed by restoration-ETA date: {len(sw)}');E(f'Planned-work notification groups keyed by scheduled date: {len(pl)}');E('')
 E('Building-level union of curated emergency groups (deduplicated across both resident archives):')
 st=gap_stats(em)
 if st:E(f'  mean gap={display(st[0],12)} d; median={display(st[1])} d; min={st[2]} d; max={st[3]} d')
 E('  CAUTION: after SITE_B begins, two resident archives can detect notifications; this union is not a constant-ascertainment incidence series.');E('')
 E('Per-source emergency ETA-date gaps (same building; descriptive notification gaps):')
 labels={'SITE_A':'neighbor archive, starts 2024','SITE_B':'repository-owner archive, starts 2025'}
 for sid in ('SITE_A','SITE_B'):
  st=gap_stats([r for r in em if source_in(r,sid)])
  if st:E(f"  {sid} ({labels[sid]}): mean={display(st[0])} d; median={display(st[1])} d; min={st[2]} d; max={st[3]} d")
 E("  Do not restate these values as 'an outage every N days': SMS completeness and physical incident identity are not established.");E('')
 def ay(y):
  s,e=date(y,1,1),date(y,8,6);return sum(source_in(r,'SITE_A') and s<=r['anchor_date']<=e for r in em)
 n25,n26=ay(2025),ay(2026);ratio=Fraction(n26,n25);chg=(ratio-1)*100
 E('Same-source descriptive comparison (SITE_A / neighbor archive; same Orkhevi building; Jan 1-Aug 6):');E(f'  2025: {n25} emergency ETA-date groups');E(f'  2026: {n26} emergency ETA-date groups');E(f'  exact descriptive ratio: {display(ratio)}');E(f'  exact relative change: {display(chg,6)}%');E('  This is an Orkhevi-building resident notification series, not a complete building-wide physical-outage rate.');E('')
 start=date(2025,12,6);a={r['anchor_date'] for r in em if source_in(r,'SITE_A') and start<=r['anchor_date']<=re};b={r['anchor_date'] for r in em if source_in(r,'SITE_B') and start<=r['anchor_date']<=re};sh=a&b;u=a|b
 E(f'Cross-resident emergency ETA-date overlap at the same building ({start}..{re}):');E(f'  SITE_A unique ETA dates: {len(a)}');E(f'  SITE_B unique ETA dates: {len(b)}');E(f'  shared ETA dates: {len(sh)}');E(f'  Jaccard(unique ETA-date sets): {display(Fraction(len(sh),len(u)))}');E('  Interpretation: corroboration between two resident archives for one building; not two-site/network-topology evidence.');E('')
 sel=[r for r in pl if r['status'] in {'announced','announced_with_possible_undated_update'}];hrs=[Fraction(r['scheduled_window_hours_explicit']) for r in sel if r['scheduled_window_hours_explicit']];tot=sum(hrs,Fraction());med=sorted(hrs)[len(hrs)//2]
 E(f'Explicit scheduled windows without a cancellation signal in the same group: {len(sel)} groups, {display(tot)} announced hours');E(f'  announced-window exact mean={display(tot/len(hrs))} h; median={display(med)} h');E('  These are notice-window hours, not verified downtime.');E('')
 br=[r for r in em if source_in(r,'SITE_B')];bs,be=min(r['anchor_date'] for r in br),max(r['anchor_date'] for r in br);E('SITE_B / repository-owner archive fully-contained calendar-window maxima:')
 for w in (3,7,14,24,30):
  z=fully_contained_window_max(br,w,bs,be)
  if z:
   c,s,e,x=z;det=', '.join(f"{r['anchor_date']}({r['group_id']})" for r in x);E(f'  {w:2d}-day window: max {c} groups, {s}..{e}: {det}')
 E('');E('Interpretation: 4-6 Aug are three emergency notification groups in the repository-owner archive for the same building on three consecutive ETA dates; this is not by itself proof of three distinct physical outage incidents.')
 return '\n'.join(out)+'\n'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output');a=ap.parse_args();t=render();print(t,end='')
 if a.output:
  p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
