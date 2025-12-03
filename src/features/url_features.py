import re
import pandas as pd
from urllib.parse import urlparse

IP_RE = re.compile(r'://\d+\.\d+\.\d+\.\d+')


def extract_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple URL-based features."""
    df = df.copy()

    def has_ip(u): 
        return int(bool(IP_RE.search(str(u))))

    def num_digits(u): 
        return sum(c.isdigit() for c in str(u))

    def count_subdirs(u): 
        return str(u).count('/')

    def count_dashes(u): 
        return str(u).count('-')

    def has_at(u): 
        return int('@' in str(u))

    def len_url(u): 
        return len(str(u))

    def tld(u):
        try:
            netloc = urlparse(str(u)).netloc
            return netloc.split('.')[-1]
        except Exception:
            return ""

    df["len"] = df["url"].apply(len_url)
    df["has_ip"] = df["url"].apply(has_ip)
    df["digits"] = df["url"].apply(num_digits)
    df["subdirs"] = df["url"].apply(count_subdirs)
    df["dashes"] = df["url"].apply(count_dashes)
    df["has_at"] = df["url"].apply(has_at)
    df["tld"] = df["url"].apply(tld)

    return df
