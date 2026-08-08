#!/usr/bin/env python3
"""Exact arithmetic for descriptive SMS-notification rate comparisons.

SITE_A and SITE_B are stable legacy identifiers for two resident SMS archives
from the same Orkhevi building, not two geographic sites. SITE_A is the
neighbor's longer archive (supplied from 2024); SITE_B is the repository
owner's archive (supplied from 2025).

Canonical values are reduced fractions. Decimal strings are presentation only.
This script does not estimate SAIDI/SAIFI or a true physical-outage rate.
"""
from __future__ import annotations
import argparse, csv, json
from datetime import date
from decimal import Decimal, localcontext, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_GROUPS=ROOT/'data'/'derived'/'notification_groups.csv'
DEFAULT_WBES=ROOT/'data'/'benchmarks'/'wbes_tbilisi_2023.json'
DAYS_PER_GREGORIAN_YEAR=Fraction(146097,400)
DAYS_PER_GREGORIAN_MONTH=DAYS_PER_GREGORIAN_YEAR/12
SOURCE_LABELS={
    'SITE_A': "neighbor resident archive (same building; longer record, starts 2024)",
    'SITE_B': "repository-owner resident archive (same building; starts 2025)",
}
def fraction_text(v): return str(v.numerator) if v.denominator==1 else f'{v.numerator}/{v.denominator}'
def terminating_decimal(v):
    d=v.denominator; a=b=0
    while d%2==0: d//=2; a+=1
    while d%5==0: d//=5; b+=1
    if d!=1:return None
    p=max(a,b); s=v*(10**p); assert s.denominator==1
    if p==0:return str(s.numerator)
    sign='-' if s.numerator<0 else ''; digits=str(abs(s.numerator)).rjust(p+1,'0')
    return f'{sign}{digits[:-p]}.{digits[-p:]}'
def rounded_decimal(v,places=12):
    q=Decimal(1).scaleb(-places)
    with localcontext() as c:
        c.prec=max(50,places+30); x=Decimal(v.numerator)/Decimal(v.denominator)
        return format(x.quantize(q,rounding=ROUND_HALF_UP),'f')
def payload(v): return {'numerator':v.numerator,'denominator':v.denominator,'exact_fraction':fraction_text(v),'exact_decimal':terminating_decimal(v),'decimal_12dp_rounded':rounded_decimal(v,12)}
def load_groups(path):
    out=[]
    with path.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f): r['anchor_date']=date.fromisoformat(r['anchor_date']); out.append(r)
    if not out: raise ValueError('no groups')
    return out
def source_in(r,s): return s in r['evidence_sites'].split(';')
def median_int(vals):
    o=sorted(vals); m=len(o)//2
    return Fraction(o[m],1) if len(o)%2 else Fraction(o[m-1]+o[m],2)
def gap_metrics(rows):
    o=sorted(rows,key=lambda r:(r['anchor_date'],r['group_id']))
    if len(o)<2: raise ValueError('need >=2 rows')
    gaps=[(b['anchor_date']-a['anchor_date']).days for a,b in zip(o,o[1:])]
    elapsed=(o[-1]['anchor_date']-o[0]['anchor_date']).days
    assert sum(gaps)==elapsed
    n=len(gaps); mean=Fraction(elapsed,n)
    return {'group_count':len(o),'first_anchor_date':o[0]['anchor_date'].isoformat(),'last_anchor_date':o[-1]['anchor_date'].isoformat(),'elapsed_days_between_first_and_last_anchor':elapsed,'interarrival_interval_count':n,'gaps_days':gaps,'mean_gap_days':payload(mean),'median_gap_days':payload(median_int(gaps)),'min_gap_days':min(gaps),'max_gap_days':max(gaps),'standardized_interarrival_groups_per_30_days':payload(Fraction(n,elapsed)*30),'standardized_interarrival_groups_per_mean_gregorian_month':payload(Fraction(n,elapsed)*DAYS_PER_GREGORIAN_MONTH)}
def equal_period(emergency):
    def c(y):
        s,e=date(y,1,1),date(y,8,6); return sum(source_in(r,'SITE_A') and s<=r['anchor_date']<=e for r in emergency)
    a,b=c(2025),c(2026); ratio=Fraction(b,a); ch=ratio-1
    return {'period':'Jan 1 through Aug 6 inclusive','2025_group_count':a,'2026_group_count':b,'count_ratio_2026_over_2025':payload(ratio),'relative_change':payload(ch),'relative_change_percent':payload(ch*100)}
def cross_resident_overlap(emergency):
    start=date(2025,12,6); end=max(r['anchor_date'] for r in emergency)
    a={r['anchor_date'] for r in emergency if source_in(r,'SITE_A') and start<=r['anchor_date']<=end}
    b={r['anchor_date'] for r in emergency if source_in(r,'SITE_B') and start<=r['anchor_date']<=end}
    u=a|b; sh=a&b
    return {'start':start.isoformat(),'end':end.isoformat(),'source_a_unique_eta_dates':len(a),'source_b_unique_eta_dates':len(b),'shared_eta_dates':len(sh),'union_eta_dates':len(u),'jaccard':payload(Fraction(len(sh),len(u)))}
def planned(rows):
    selected=[r for r in rows if r['category']=='planned' and r['status'] in {'announced','announced_with_possible_undated_update'} and r['scheduled_window_hours_explicit']]
    hrs=[Fraction(r['scheduled_window_hours_explicit']) for r in selected]; total=sum(hrs,Fraction())
    o=sorted(hrs); m=len(o)//2; med=o[m] if len(o)%2 else (o[m-1]+o[m])/2
    return {'group_count':len(hrs),'total_announced_hours':payload(total),'mean_announced_hours':payload(total/len(hrs)),'median_announced_hours':payload(med)}
def comparison(metrics,wbes_rate):
    m=metrics['standardized_interarrival_groups_per_mean_gregorian_month']; r=Fraction(m['numerator'],m['denominator'])
    ratio=r/wbes_rate; excess=ratio-1
    return {'mean_gregorian_month_interarrival_rate':payload(r),'wbes_published_typical_month_rate_from_display':payload(wbes_rate),'ratio_over_wbes_display':payload(ratio),'relative_excess_over_wbes_display':payload(excess),'relative_excess_percent_over_wbes_display':payload(excess*100)}
def build_analysis(groups_path,wbes_path):
    rows=load_groups(groups_path); emergency=[r for r in rows if r['category']=='emergency']
    a=[r for r in emergency if source_in(r,'SITE_A')]; b=[r for r in emergency if source_in(r,'SITE_B')]
    ma,mb,building=gap_metrics(a),gap_metrics(b),gap_metrics(emergency)
    w=json.loads(wbes_path.read_text(encoding='utf-8')); wt=str(w['indicators']['bready_in2']['published_value']); wr=Fraction(wt)
    return {'schema_version':2,'source_identity':{'SITE_A':SOURCE_LABELS['SITE_A'],'SITE_B':SOURCE_LABELS['SITE_B'],'relationship':'same Orkhevi building; separate resident/subscriber SMS archives','legacy_identifier_warning':'SITE_A/SITE_B are retained for stable references but must not be interpreted as two geographic sites.'},'metric_scope_warning':'Emergency rows are curated restoration-ETA notification groups, not proven distinct physical outages. Archive completeness is not established.','calendar_constants':{'mean_gregorian_year_days':payload(DAYS_PER_GREGORIAN_YEAR),'mean_gregorian_month_days':payload(DAYS_PER_GREGORIAN_MONTH)},'source_a_emergency_interarrival':ma,'source_b_emergency_interarrival':mb,'building_union_emergency_interarrival':building,'source_a_equal_period_comparison':equal_period(emergency),'cross_resident_overlap':cross_resident_overlap(emergency),'planned_windows':planned(rows),'wbes_tbilisi_2023':{'source':w.get('source'),'source_endpoint':w.get('source_endpoint'),'published_average_outages_typical_month_text':wt,'published_average_outages_typical_month_fraction_from_display':payload(wr),'precision_warning':'The rational form exactly represents the decimal string published by WBES; it is not the hidden unrounded weighted survey estimate.'},'benchmark_comparisons':{'primary_long_single_source_a':comparison(ma,wr),'secondary_building_union':comparison(building,wr),'secondary_recent_source_b':comparison(mb,wr)},'comparison_policy':'Primary benchmark comparison uses SITE_A because it is the longest single-resident series with a stable source. The building union is secondary because source ascertainment changes when SITE_B begins; SITE_B is a shorter recent series.'}
def render_text(d):
    a=d['source_a_emergency_interarrival']; b=d['source_b_emergency_interarrival']; u=d['building_union_emergency_interarrival']; y=d['source_a_equal_period_comparison']; o=d['cross_resident_overlap']; p=d['planned_windows']; w=d['wbes_tbilisi_2023']; c=d['benchmark_comparisons']
    def lm(name,m):
        gap=m['mean_gap_days']; rate=m['standardized_interarrival_groups_per_mean_gregorian_month']
        gaptext=gap['exact_fraction']+(f" = {gap['exact_decimal']}" if gap['exact_decimal'] else f" (decimal rounded to 12 dp: {gap['decimal_12dp_rounded']})")
        return [name,f"  groups: {m['group_count']}",f"  first..last anchor: {m['first_anchor_date']} .. {m['last_anchor_date']}",f"  elapsed days: {m['elapsed_days_between_first_and_last_anchor']}",f"  inter-arrival intervals: {m['interarrival_interval_count']}",f"  exact mean gap: {gaptext} days",f"  exact mean-Gregorian-month normalized rate: {rate['exact_fraction']} (decimal rounded to 12 dp: {rate['decimal_12dp_rounded']})"]
    L=['Exact descriptive rate analysis','===============================','',d['source_identity']['relationship']+'.',d['source_identity']['legacy_identifier_warning'],d['metric_scope_warning'],'']
    L+=lm('SITE_A / neighbor resident archive (same building; longest single-source record):',a)+['']
    L+=lm('SITE_B / repository-owner resident archive (same building; shorter recent record):',b)+['']
    L+=lm('Building-level union of curated emergency groups (deduplicated across the two resident archives):',u)+['  CAUTION: this union changes ascertainment when the second resident archive begins, so it is secondary to the long single-source series.','']
    L += ['SITE_A equal-period count comparison (Jan 1-Aug 6):',f"  2025: {y['2025_group_count']}",f"  2026: {y['2026_group_count']}",f"  exact ratio: {y['count_ratio_2026_over_2025']['exact_fraction']}",f"  exact relative change percent: {y['relative_change_percent']['exact_fraction']}% (decimal rounded to 12 dp: {y['relative_change_percent']['decimal_12dp_rounded']}%)",'', 'Cross-resident overlap at the same building:',f"  SITE_A unique ETA dates: {o['source_a_unique_eta_dates']}",f"  SITE_B unique ETA dates: {o['source_b_unique_eta_dates']}",f"  shared ETA dates: {o['shared_eta_dates']}",f"  exact Jaccard: {o['jaccard']['exact_fraction']} (decimal rounded to 12 dp: {o['jaccard']['decimal_12dp_rounded']})",'  Interpretation: corroboration between two resident SMS archives for the same building; not evidence about two separate service points or network topology.','', 'Planned announced windows:',f"  groups: {p['group_count']}",f"  exact total hours: {p['total_announced_hours']['exact_fraction']}",f"  exact mean hours: {p['mean_announced_hours']['exact_fraction']}",f"  exact median hours: {p['median_announced_hours']['exact_fraction']}",'', 'WBES Tbilisi 2023:',f"  published average outages in a typical month: {w['published_average_outages_typical_month_text']}",f"  exact rational representation of displayed value: {w['published_average_outages_typical_month_fraction_from_display']['exact_fraction']}",w['precision_warning'],'']
    for label,x in [('PRIMARY — long single-source SITE_A',c['primary_long_single_source_a']),('SECONDARY — building union',c['secondary_building_union']),('SECONDARY — shorter recent SITE_B',c['secondary_recent_source_b'])]:
        L += [label+':',f"  normalized monthly notification rate: {x['mean_gregorian_month_interarrival_rate']['exact_fraction']} (decimal rounded to 12 dp: {x['mean_gregorian_month_interarrival_rate']['decimal_12dp_rounded']})",f"  ratio to displayed WBES 0.8: {x['ratio_over_wbes_display']['exact_fraction']} (decimal rounded to 12 dp: {x['ratio_over_wbes_display']['decimal_12dp_rounded']})",f"  relative excess: {x['relative_excess_percent_over_wbes_display']['exact_fraction']}% (decimal rounded to 12 dp: {x['relative_excess_percent_over_wbes_display']['decimal_12dp_rounded']}%)",'']
    L += [d['comparison_policy'],'These are notification/inter-arrival proxies, not a statistically rigorous building-vs-Tbilisi physical-outage reliability ratio.','Do not rewrite these metrics as SAIFI or as proven physical-outage frequency.']
    return '\n'.join(L)+'\n'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--groups',type=Path,default=DEFAULT_GROUPS); ap.add_argument('--wbes',type=Path,default=DEFAULT_WBES); ap.add_argument('--output-json',type=Path); ap.add_argument('--output-text',type=Path); a=ap.parse_args(); d=build_analysis(a.groups,a.wbes); t=render_text(d); print(t,end='')
    if a.output_json: a.output_json.parent.mkdir(parents=True,exist_ok=True); a.output_json.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    if a.output_text: a.output_text.parent.mkdir(parents=True,exist_ok=True); a.output_text.write_text(t,encoding='utf-8',newline='\n')
    return 0
if __name__=='__main__': raise SystemExit(main())
