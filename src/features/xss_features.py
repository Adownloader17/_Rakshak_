# src/features/xss_features.py
import pandas as pd
import re

EVENT_HANDLER_RE = re.compile(r'on\w+\s*=' , re.IGNORECASE)

def extract_xss_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Ensure column name 'payload' exists
    if 'payload' not in df.columns:
        # try other names
        if 'url' in df.columns:
            df['payload'] = df['url']
        else:
            raise KeyError("No 'payload' or 'url' column found in dataframe")

    s = df['payload'].astype(str)

    df['len'] = s.str.len()
    df['num_script'] = s.str.count(r'(?i)<\s*script')
    df['num_iframe'] = s.str.count(r'(?i)<\s*iframe')
    df['num_on_events'] = s.apply(lambda x: len(EVENT_HANDLER_RE.findall(x)))
    df['num_js_proto'] = s.str.count(r'(?i)javascript:')
    df['num_eval'] = s.str.count(r'(?i)\beval\s*\(')
    df['num_alert'] = s.str.count(r'(?i)alert\s*\(')
    df['num_tags'] = s.str.count(r'<')
    df['num_quotes'] = s.str.count(r'["\']')
    # ratio features (avoid division by zero)
    df['tags_ratio'] = df['num_tags'] / (df['len'] + 1)
    return df
