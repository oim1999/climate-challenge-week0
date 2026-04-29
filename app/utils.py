import pandas as pd
import numpy as np
from scipy import stats
import os

def load_data(countries: list[str], data_dir: str = None) -> pd.DataFrame:
    """Load and combine cleaned CSV files for the specified countries."""
    if data_dir is None:
        # Find the 'data' folder relative to this script's location
        # __file__ is app/utils.py, so dirname is app/, and dirname of that is project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, "data")
        
    file_map = {
        "Ethiopia": os.path.join(data_dir, "../data/ethiopia_clean.csv"),
        "Tanzania": os.path.join(data_dir, "../data/tanzania_clean.csv"),
        "Sudan": os.path.join(data_dir, "../data/sudan_clean.csv"),
        "Kenya": os.path.join(data_dir, "../data/kenya_clean.csv"),
        "Uganda": os.path.join(data_dir, "../data/uganda_clean.csv"),
    }
    
    frames = []
    for country in countries:
        path = file_map.get(country)
        if path and os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["Date"])
            df["Country"] = country
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def summary_table(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Return a summary table with mean, median, and std per country."""
    agg = df.groupby("Country")[metrics].agg(["mean", "median", "std"]).round(2)
    agg.columns = [f"{col}_{stat}" for col, stat in agg.columns]
    return agg


def top_regions(df: pd.DataFrame, metric: str = "GHI", top_n: int = 3) -> pd.DataFrame:
    """Return countries ranked by average of the given metric."""
    ranked = (
        df.groupby("Country")[metric]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
    )
    ranked.columns = ["Country", f"Average {metric} (W/m²)"]
    return ranked.head(top_n)


def run_anova(df: pd.DataFrame, metric: str = "GHI") -> dict:
    """Run a one-way ANOVA on the given metric across countries."""
    groups = [
        group[metric].dropna().values
        for _, group in df.groupby("Country")
    ]
    if not groups:
        return {"f_stat": 0, "p_value": 1.0}
    f_stat, p_value = stats.f_oneway(*groups)
    return {"f_stat": round(f_stat, 4), "p_value": p_value}


def daily_average(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Resample data to daily averages per country."""
    df = df.copy()
    df = df.set_index("Date")
    daily = (
        df.groupby("Country")[metric]
        .resample("D")
        .mean()
        .reset_index()
    )
    return daily
