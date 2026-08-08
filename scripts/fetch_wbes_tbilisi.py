#!/usr/bin/env python3
"""Fetch and normalize the official WBES 2023 Tbilisi infrastructure subgroup.

The raw response is preserved byte-for-byte. Published decimal strings are also
preserved verbatim; any fraction emitted by this tool is only the exact rational
representation of the displayed API string, not an unrounded survey estimate.

WBES "typical month" is preserved as a survey concept and is not silently
reinterpreted as an arithmetic mean Gregorian calendar month.
"""
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from urllib.request import Request,urlopen
DEFAULT_URL='https://extdataportal.worldbank.org/api/esapi/GetEconomyCutsData/economyid/74/year/2023/topicid/8/cutsid/3/?lang=en'
SOURCE_TOPIC_PAGE='https://www.enterprisesurveys.org/en/data/exploretopics/infrastructure-and-climate'
SOURCE_MICRODATA_C7='https://microdata.worldbank.org/catalog/6443/variable/F1/V57?name=c7'
DEFAULT_OUTPUT_DIR=Path('artifacts/wbes/tbilisi-2023')
WANTED_FIELDS={'in16':'Percent of firms experiencing electrical outages','bready_in2':'[B-READY] Average number of electrical outages in a typical month','bready_in3_median':'[B-READY] Duration, in hours, of a typical electrical outage [median]','in12':'Percent of firms identifying electricity as a major or very severe constraint','bready_in9':'[B-READY] Percent of firms owning or sharing a generator'}
TYPICAL_MONTH_NOTE=("WBES 'typical month' is a survey concept, not an arithmetic mean Gregorian calendar month. ""The published typical-month value cannot be exactly converted to 'one outage every N days' and is not definition-identical to resident emergency restoration-ETA notification inter-arrival metrics.")
COMPARISON_POLICY='Use WBES as independent Tbilisi context; do not report a direct X-times or percentage physical-outage reliability ratio against resident calendar inter-arrival normalizations.'
def exact_fraction_from_display(text):
 v=Fraction(text);return {'numerator':v.numerator,'denominator':v.denominator,'exact_fraction_from_display':str(v.numerator) if v.denominator==1 else f'{v.numerator}/{v.denominator}'}
def fetch(url,timeout):
 req=Request(url,headers={'Accept':'application/json','User-Agent':'telasi-orkhevi-settlement-outage-analysis/1.0 (+reproducible research)'},method='GET')
 with urlopen(req,timeout=timeout) as r:
  body=r.read();meta={'http_status':r.status,'content_type':r.headers.get('Content-Type'),'date_header':r.headers.get('Date')}
 return body,meta
def normalize(raw,source_url,fetched_at):
 data=json.loads(raw.decode('utf-8-sig'))
 if not isinstance(data,list):raise ValueError('WBES endpoint response is not a JSON list')
 rows=[r for r in data if isinstance(r,dict) and r.get('subCut')=='Tbilisi']
 if not rows:raise ValueError('No Tbilisi subgroup rows found')
 by={}
 for r in rows:
  f=r.get('queryFieldName')
  if isinstance(f,str):
   if f in by:raise ValueError(f'Duplicate Tbilisi queryFieldName: {f}')
   by[f]=r
 missing=sorted(set(WANTED_FIELDS)-set(by))
 if missing:raise ValueError('Missing expected Tbilisi indicators: '+', '.join(missing))
 indicators={}
 for f,label in WANTED_FIELDS.items():
  r=by[f];actual=r.get('indicator')
  if actual!=label:raise ValueError(f'Tbilisi indicator label changed for {f}: expected {label!r}, got {actual!r}')
  published=r.get('country')
  if not isinstance(published,str):raise ValueError(f'Tbilisi indicator {f} country value is not a JSON string; refusing to claim lexical precision')
  indicators[f]={'indicator_id':r.get('indicatorId'),'query_field_name':f,'indicator':actual,'published_value':published,**exact_fraction_from_display(published)}
 return {'schema_version':1,'source':'World Bank Enterprise Surveys','economy':'Georgia','survey_year':2023,'topic_id':8,'cut_id':3,'cut':'Location','subcut':'Tbilisi','source_endpoint':source_url,'source_topic_page':SOURCE_TOPIC_PAGE,'source_microdata_variable_c7':SOURCE_MICRODATA_C7,'fetched_at_utc':fetched_at,'raw_response_bytes':len(raw),'raw_response_sha256':hashlib.sha256(raw).hexdigest(),'tbilisi_row_count':len(rows),'precision_note':'WBES API values are published/display values with finite decimal precision. Rational forms exactly represent returned decimal strings; they do not recover hidden unrounded weighted survey estimates.','typical_month_semantics_note':TYPICAL_MONTH_NOTE,'comparison_policy':COMPARISON_POLICY,'indicators':indicators}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--url',default=DEFAULT_URL);ap.add_argument('--output-dir',type=Path,default=DEFAULT_OUTPUT_DIR);ap.add_argument('--timeout',type=int,default=60);a=ap.parse_args();fetched_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z');raw,http=fetch(a.url,a.timeout);n=normalize(raw,a.url,fetched_at);a.output_dir.mkdir(parents=True,exist_ok=True);rp=a.output_dir/'wbes-tbilisi-topic8-location-cuts.raw.json';np=a.output_dir/'wbes-tbilisi-benchmark.json';mp=a.output_dir/'wbes-tbilisi-fetch-metadata.json';rp.write_bytes(raw);np.write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');meta={'source_endpoint':a.url,'source_topic_page':SOURCE_TOPIC_PAGE,'source_microdata_variable_c7':SOURCE_MICRODATA_C7,'fetched_at_utc':fetched_at,**http,'raw_response_bytes':len(raw),'raw_response_sha256':n['raw_response_sha256'],'typical_month_semantics_note':TYPICAL_MONTH_NOTE,'comparison_policy':COMPARISON_POLICY,'raw_file':rp.name,'normalized_file':np.name};mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(f'Fetched {a.url}');print(f"Raw bytes: {len(raw)}");print(f"Raw SHA-256: {n['raw_response_sha256']}")
 for f in WANTED_FIELDS:
  x=n['indicators'][f];print(f"{f}: {x['published_value']} (exact fraction from displayed value: {x['exact_fraction_from_display']})")
 print("WBES typical-month values are not converted to a fixed day interval.");print(f'Wrote {rp}');print(f'Wrote {np}');print(f'Wrote {mp}');return 0
if __name__=='__main__':raise SystemExit(main())
