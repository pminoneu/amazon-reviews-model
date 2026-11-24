"""Independently check target labels, baseline arithmetic, and the sampled raw row."""
from pathlib import Path
import csv
import gzip
import hashlib
import json
import math
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'results'
a=json.loads((OUT/'audit.json').read_text())
with (OUT/'product_summary.csv').open(newline='') as f:rows=list(csv.DictReader(f))
train=[r for r in rows if r['split']=='train'];test=[r for r in rows if r['split']=='test']
assert len(rows)==a['eligible_products']
assert len({r['parent_asin'] for r in rows})==len(rows)
assert len(train)==a['train_n'] and len(test)==a['test_n']
sorted_counts=sorted(int(r['later_review_count_365d']) for r in train)
q_index=(len(sorted_counts)-1)*.75
lo,hi=math.floor(q_index),math.ceil(q_index)
threshold=sorted_counts[lo]+(q_index-lo)*(sorted_counts[hi]-sorted_counts[lo])
assert threshold==a['future_count_threshold_training_q75']
for r in rows:
    count=int(r['later_review_count_365d'])
    rating=float(r['later_rating_mean_365d']) if r['later_rating_mean_365d'] else float('nan')
    expected=int(count>=threshold and rating>=4)
    assert expected==int(r['is_successful'])
assert sum(int(r['is_successful']) for r in rows)==a['target_positive']
positive=sum(int(r['is_successful']) for r in test)
negative=len(test)-positive
assert a['baseline']['tn']==negative and a['baseline']['fn']==positive
assert a['baseline']['fp']==0 and a['baseline']['tp']==0
assert math.isclose(a['baseline']['accuracy'],negative/len(test))
assert math.isclose(a['baseline']['balanced_accuracy'],.5)
for name,meta in a['sources'].items():
    with (BASE/'data'/name).open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    assert actual==meta['sha256'],f'Source hash mismatch: {name}'
sample=a['random_row'];seen=set();records=[]
with gzip.open(BASE/'data/All_Beauty.jsonl.gz','rt',encoding='utf-8') as f:
    for order,line in enumerate(f):
        r=json.loads(line)
        if r['parent_asin']!=sample['parent_asin']:continue
        key=json.dumps(r,sort_keys=True)
        if key in seen:continue
        seen.add(key);records.append((r['timestamp'],order,r))
records.sort();early=records[:20];cutoff=early[-1][0]
late=[r for ts,order,r in records if cutoff<ts<=cutoff+365*86400000]
assert cutoff==sample['cutoff_timestamp']
assert math.isclose(sum(r['rating'] for ts,order,r in early)/20,sample['early_rating_mean'])
assert math.isclose(sum(r['verified_purchase'] for ts,order,r in early)/20,sample['early_verified_share'])
assert len(late)==sample['later_review_count_365d']
assert math.isclose(sum(r['rating'] for r in late)/len(late),sample['later_rating_mean_365d'])
result={'target_rules_checked':len(rows),'unique_products':len(rows),'train_products':len(train),'test_products':len(test),'training_q75':threshold,'baseline_balanced_accuracy_direct':.5,'baseline_accuracy_direct':negative/len(test),'raw_source_hashes':'passed','sample_product':sample['parent_asin'],'sample_features_and_outcome':'recomputed from raw source and matched','status':'passed'}
(OUT/'package_verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
