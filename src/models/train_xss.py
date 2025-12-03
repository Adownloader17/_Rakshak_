# src/models/train_xss.py
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from joblib import dump
from src.features.xss_features import extract_xss_features

def load_data(path="data/raw/xss_data.csv"):
    df = pd.read_csv(path)
    # expect 'payload' and 'label' (0/1 or clean/malicious)
    return df

def normalize_label(series):
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).astype(int).apply(lambda x: 1 if x != 0 else 0)
    s = series.astype(str).str.lower().str.strip()
    mapping = {"malicious":1,"xss":1,"attack":1,"1":1,"true":1,"yes":1,
               "clean":0,"benign":0,"0":0,"false":0,"no":0,"legit":0}
    mapped = s.map(lambda x: mapping.get(x, None))
    if mapped.isnull().any():
        # if only two unique values, map minority -> 1
        counts = s.value_counts()
        if len(counts)==2:
            most = counts.idxmax()
            mapped = s.apply(lambda x: 0 if x==most else 1)
        else:
            raise ValueError(f"Unhandled label values: {sorted(s.unique())}")
    return mapped.astype(int)

def main():
    df = load_data()
    df = extract_xss_features(df)
    feature_cols = ['len','num_script','num_iframe','num_on_events','num_js_proto',
                    'num_eval','num_alert','num_tags','num_quotes','tags_ratio']
    X = df[feature_cols]
    y = normalize_label(df['label'])
    print("Class distribution:\n", y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    dtrain = lgb.Dataset(X_train, label=y_train)
    params = {'objective':'binary','metric':'binary_logloss','boosting_type':'gbdt'}
    model = lgb.train(params, dtrain, num_boost_round=200)
    preds = (model.predict(X_test) > 0.5).astype(int)
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))
    dump(model, 'src/models/xss_model.joblib')
    print("Saved xss_model.joblib")

if __name__=='__main__':
    main()
