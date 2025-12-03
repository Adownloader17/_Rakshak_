import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from joblib import dump

from src.features.url_features import extract_basic_features


def load_data():
    df = pd.read_csv("data/raw/malicious_phish.csv")
    df = df.rename(columns={"url": "url", "label": "label"})
    return df


def preprocess(df):
    df = extract_basic_features(df)

    feature_cols = ["len", "has_ip", "digits", "subdirs", "dashes", "has_at"]

    X = df[feature_cols]

    # Convert label: bad = 1, good = 0
    y = df["label"].apply(lambda x: 1 if x == "bad" else 0)

    return X, y


def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    train_data = lgb.Dataset(X_train, label=y_train)

    params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "boosting_type": "gbdt",
    }

    model = lgb.train(params, train_data, num_boost_round=150)

    preds = model.predict(X_test)
    preds_binary = (preds > 0.5).astype(int)

    print("\nAccuracy:", accuracy_score(y_test, preds_binary))
    print("\nClassification Report:\n", classification_report(y_test, preds_binary))

    return model


def save_model(model):
    dump(model, "src/models/phishing_model.joblib")
    print("Model saved at src/models/phishing_model.joblib")


if __name__ == "__main__":
    df = load_data()
    X, y = preprocess(df)
    model = train_model(X, y)
    save_model(model)
