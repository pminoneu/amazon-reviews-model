"""Reproduce the proposal's data audit and no-input baseline (no feature model)."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'assignment6-mpl'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, precision_score, recall_score, f1_score

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'results'
OUT.mkdir(exist_ok=True)
DAY = 86_400_000
SOURCES = {
    'All_Beauty.jsonl.gz': 'https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/All_Beauty.jsonl.gz',
    'meta_All_Beauty.jsonl.gz': 'https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_All_Beauty.jsonl.gz',
}

rows, hashes, duplicate_count = [], set(), 0
with gzip.open(BASE / 'data' / 'All_Beauty.jsonl.gz', 'rt') as f:
    for order, line in enumerate(f):
        item = json.loads(line)
        digest = hashlib.sha256(json.dumps(item, sort_keys=True).encode()).digest()
        duplicate_count += digest in hashes
        hashes.add(digest)
        rows.append({k: item.get(k) for k in ['parent_asin', 'asin', 'user_id', 'timestamp', 'rating', 'verified_purchase', 'text'] } | {'source_order': order, 'record_digest':digest})
r = pd.DataFrame(rows)
del rows, hashes
print('Loaded reviews', len(r), flush=True)
meta_rows = []
with gzip.open(BASE / 'data' / 'meta_All_Beauty.jsonl.gz', 'rt') as f:
    for line in f:
        item = json.loads(line)
        meta_rows.append({k:item.get(k) for k in ['parent_asin', 'title', 'price', 'main_category']})
m = pd.DataFrame(meta_rows)
del meta_rows

assert r[['parent_asin','timestamp','rating','verified_purchase']].notna().all().all()
assert r.rating.between(1,5).all()
raw_review_n, raw_product_n = len(r), r.parent_asin.nunique()
r = r.drop_duplicates('record_digest', keep='first').copy()
assert raw_review_n-len(r) == duplicate_count
print('Removed exact repeated records', duplicate_count, flush=True)
assert m.parent_asin.is_unique
r = r.sort_values(['parent_asin','timestamp','source_order'], kind='stable')
r['review_order'] = r.groupby('parent_asin').cumcount() + 1
counts = r.groupby('parent_asin').size()
end = int(r.timestamp.max())
t20 = r[r.review_order.eq(20)].set_index('parent_asin').timestamp
eligible = t20[t20 + 365 * DAY <= end]
cutoff_ties = r[r.review_order.gt(20)].join(eligible.rename('cutoff_timestamp'), on='parent_asin')
cutoff_ties = int(cutoff_ties.timestamp.eq(cutoff_ties.cutoff_timestamp).sum())
e = r[r.parent_asin.isin(eligible.index)].copy()
e = e.join(eligible.rename('cutoff_timestamp'), on='parent_asin')
early = e[e.review_order.le(20)]
later = e[(e.timestamp > e.cutoff_timestamp) & (e.timestamp <= e.cutoff_timestamp + 365*DAY)]
f = pd.DataFrame(index=eligible.index)
f['cutoff_timestamp'] = eligible
f['cutoff_utc'] = pd.to_datetime(eligible, unit='ms', utc=True).astype(str)
g = early.groupby('parent_asin')
f['early_rating_mean'] = g.rating.mean()
f['days_to_20'] = (eligible - g.timestamp.min()) / DAY
f['early_verified_share'] = g.verified_purchase.mean()
f['early_low_rating_share'] = g.rating.apply(lambda x: x.le(2).mean())
f['early_text'] = g.text.apply(lambda x: '\n'.join(x.fillna('')))
f['later_review_count_365d'] = later.groupby('parent_asin').size().reindex(f.index).fillna(0).astype(int)
f['later_rating_mean_365d'] = later.groupby('parent_asin').rating.mean()
f = f.sort_index()
train_ids, test_ids = train_test_split(f.index.to_numpy(), test_size=.30, random_state=42)
threshold = float(f.loc[train_ids, 'later_review_count_365d'].quantile(.75))
f['is_successful'] = (f.later_review_count_365d.ge(threshold) & f.later_rating_mean_365d.ge(4.0)).astype(int)
f['split'] = np.where(f.index.isin(train_ids), 'train', 'test')
assert not set(train_ids) & set(test_ids)
assert len(train_ids) + len(test_ids) == len(f)
assert early.groupby('parent_asin').size().eq(20).all()
assert (later.timestamp > later.cutoff_timestamp).all()
assert (later.timestamp <= later.cutoff_timestamp + 365*DAY).all()
assert f.index.is_unique
assert not f[f.later_review_count_365d.eq(0)].is_successful.any()

y_train, y_test = f.loc[train_ids,'is_successful'], f.loc[test_ids,'is_successful']
dummy = DummyClassifier(strategy='most_frequent')
dummy.fit(np.zeros((len(train_ids), 1)), y_train)
pred = dummy.predict(np.zeros((len(test_ids), 1)))
tn,fp,fn,tp = confusion_matrix(y_test,pred,labels=[0,1]).ravel()
balanced_direct = .5*(tp/(tp+fn) + tn/(tn+fp))
assert np.isclose(balanced_direct, balanced_accuracy_score(y_test,pred))
assert np.isclose(accuracy_score(y_test,pred),(tn+tp)/len(y_test))
sample = f.sample(n=1, random_state=42).iloc[0]
sample_id = str(sample.name)
sample_metadata = m.set_index('parent_asin').loc[sample_id]
sample_record = sample.drop(labels='early_text').to_dict() | {'parent_asin':sample_id, 'title':sample_metadata['title']}

audit = {
    'raw_reviews': raw_review_n, 'clean_reviews':len(r), 'raw_products': raw_product_n, 'metadata_rows': len(m),
    'raw_date_min_utc': str(pd.to_datetime(r.timestamp.min(),unit='ms',utc=True)),
    'raw_date_max_utc': str(pd.to_datetime(end,unit='ms',utc=True)),
    'raw_exact_duplicate_reviews': duplicate_count,
    'duplicate_product_user_timestamp_keys': int(r.duplicated(['parent_asin','user_id','timestamp']).sum()),
    'raw_missing_counts':r[['parent_asin','timestamp','rating','verified_purchase','text']].isna().sum().to_dict(),
    'metadata_duplicate_keys':int(m.parent_asin.duplicated().sum()),
    'metadata_price_available':int(m.price.notna().sum()),
    'metadata_price_available_share':float(m.price.notna().mean()),
    'eligible_products': len(f), 'products_ge20':int(counts.ge(20).sum()),
    'excluded_under20':int(counts.lt(20).sum()),
    'excluded_incomplete_followup':int(counts.ge(20).sum()-len(f)),
    'eligible_metadata_unmatched': int((~f.index.isin(m.parent_asin)).sum()),
    'post20_reviews_tied_at_cutoff_excluded': cutoff_ties,
    'target_positive':int(f.is_successful.sum()), 'target_negative':int((1-f.is_successful).sum()),
    'target_rate':float(f.is_successful.mean()),
    'median_days_to20':float(f.days_to_20.median()),
    'median_days_to20_floor':float(np.floor(f.days_to_20).median()),
    'no_later_reviews':int(f.later_review_count_365d.eq(0).sum()),
    'followup_days':365, 'future_count_threshold_training_q75':threshold,
    'future_count_threshold_all_q75':float(f.later_review_count_365d.quantile(.75)),
    'train_n':len(train_ids),'test_n':len(test_ids),
    'train_positive':int(y_train.sum()),'test_positive':int(y_test.sum()),
    'train_positive_rate':float(y_train.mean()),'test_positive_rate':float(y_test.mean()),
    'split_seed':42, 'split_test_fraction':.3, 'split_stratified':False,
    'baseline':{'predicted_class':int(pred[0]), 'balanced_accuracy':float(balanced_accuracy_score(y_test,pred)),
                'accuracy':float(accuracy_score(y_test,pred)), 'positive_precision_zero_division0':float(precision_score(y_test,pred,zero_division=0)),
                'positive_recall':float(recall_score(y_test,pred)), 'f1':float(f1_score(y_test,pred)),
                'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)},
    'random_row_seed':42,'random_row':sample_record,
    'sources':{name:{'url':url,'sha256':hashlib.sha256((BASE/'data'/name).read_bytes()).hexdigest()} for name,url in SOURCES.items()},
}
f.to_csv(OUT/'product_features.csv',index_label='parent_asin')
f.drop(columns='early_text').to_csv(OUT/'product_summary.csv',index_label='parent_asin')
(OUT/'audit.json').write_text(json.dumps(audit,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig, ax = plt.subplots(figsize=(7.6,1.85),dpi=180)
vals = [audit['target_negative'],audit['target_positive']]
bars=ax.barh([1,0], vals, color=['#657787','#1D6C70'],height=.48)
ax.set_yticks([1,0],['0 - Does not meet proxy','1 - Meets success proxy'])
ax.set_xlim(0, max(vals)*1.30)
for b,n in zip(bars,vals):
    ax.text(n+65,b.get_y()+b.get_height()/2,f'{n:,} ({n/len(f):.1%})',va='center',fontsize=10,fontweight='bold')
ax.set_xlabel('Eligible products',fontsize=9)
ax.set_xticks([0,1000,2000,3000,4000,5000])
ax.grid(axis='x',color='#D8DFE5',alpha=.7,lw=.6)
ax.set_axisbelow(True)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y',length=0)
fig.tight_layout(pad=.5)
fig.savefig(OUT/'target_distribution.png',dpi=220,bbox_inches='tight',facecolor='white')
plt.close(fig)
print(json.dumps({k:v for k,v in audit.items() if k not in ['sources','raw_missing_counts']}, indent=2,default=str))
