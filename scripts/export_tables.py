"""Export small, directly readable evidence tables from the existing data audit."""
from pathlib import Path
import csv
import json
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'results'
a=json.loads((OUT/'audit.json').read_text())
def save(name,cols,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
save('baseline_scores.csv',['metric','value'],[{'metric':k,'value':v} for k,v in a['baseline'].items()])
save('target_distribution.csv',['is_successful','products','share'],[
    {'is_successful':0,'products':a['target_negative'],'share':a['target_negative']/a['eligible_products']},
    {'is_successful':1,'products':a['target_positive'],'share':a['target_positive']/a['eligible_products']}])
save('dataset_overview.csv',['metric','value'],[{'metric':k,'value':a[k]} for k in ['raw_reviews','clean_reviews','raw_products','metadata_rows','raw_exact_duplicate_reviews','eligible_products','excluded_under20','excluded_incomplete_followup','train_n','test_n','train_positive','test_positive','median_days_to20','future_count_threshold_training_q75']])
save('random_product_example.csv',list(a['random_row']),[a['random_row']])
print('Exported four evidence tables to',OUT)
