
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EthioClimate COP32 Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 African Climate Analytics Dashboard")
st.caption("Historical climate data (2015–2026) — Ethiopia, Kenya, Sudan, Tanzania, Nigeria")

# ── Load data (cached so it only runs once) ──────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and concatenate all five country cleaned CSVs."""
    countries = ["ethiopia", "kenya", "sudan", "tanzania", "nigeria"]
    data_dir = Path(__file__).parent.parent / "data"
    dfs = []
    for c in countries:
        path = data_dir / f"{c}_clean.csv"
        if not path.exists():
            st.error(f"Missing file: {path}")
            continue
        df = pd.read_csv(path, parse_dates=["Date"])
        df["Country"] = c.capitalize()
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

df = load_data()

# ── Sidebar: controls ─────────────────────────────────────────────────────────
st.sidebar.header("Filters")

all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=all_countries,
    default=all_countries,
)

min_year = int(df["YEAR"].min())
max_year = int(df["YEAR"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

variable = st.sidebar.selectbox(
    "Climate variable",
    options=["T2M", "PRECTOTCORR", "RH2M", "T2M_MAX", "T2M_MIN", "WS2M"],
    index=0,
)

VAR_LABELS = {
    "T2M":         "Mean Temperature (°C)",
    "PRECTOTCORR": "Precipitation (mm/day)",
    "RH2M":        "Relative Humidity (%)",
    "T2M_MAX":     "Max Temperature (°C)",
    "T2M_MIN":     "Min Temperature (°C)",
    "WS2M":        "Wind Speed (m/s)",
}
st.sidebar.caption("Applies to tabs 1 and 2. Extreme events tab uses fixed thresholds.")

# ── Filter data ───────────────────────────────────────────────────────────────
mask = (
    df["Country"].isin(selected_countries)
    & df["YEAR"].between(*year_range)
)
filtered = df[mask].copy()

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Temperature trends",
    "🌧️ Precipitation",
    "⚡ Extreme events",
    "📊 Vulnerability ranking",
])

# ───────────────────────────────────────────────────────────────────────────────
# TAB 1: Temperature / variable trend line chart
# ───────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader(f"Monthly average {VAR_LABELS[variable]} (2015–2026)")

    monthly = (
        filtered
        .groupby(["Country", "YEAR", "MONTH"])[variable]
        .mean()
        .reset_index()
    )
    monthly["Date"] = pd.to_datetime(
        monthly["YEAR"].astype(str) + "-" + monthly["MONTH"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(12, 4))
    for country, grp in monthly.groupby("Country"):
        ax.plot(grp["Date"], grp[variable], label=country, linewidth=1.5)

    ax.set_xlabel("Year")
    ax.set_ylabel(VAR_LABELS[variable])
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    # Summary stats table
    st.markdown("**Summary statistics**")
    st.dataframe(
        filtered.groupby("Country")[variable]
        .agg(Mean="mean", Median="median", Std="std")
        .round(2)
    )

# ───────────────────────────────────────────────────────────────────────────────
# TAB 2: Precipitation boxplots
# ───────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader(f"{VAR_LABELS[variable]} distribution by country")

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.boxplot(
        data=filtered,
        x="Country",
        y=variable,
        showfliers=False,
        palette="Set2",
        ax=ax,
    )
    ax.set_ylabel(VAR_LABELS[variable])
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("**Summary statistics**")
    st.dataframe(
        filtered.groupby("Country")[variable]
        .agg(Mean="mean", Median="median", Std="std")
        .round(3)
    )

# ───────────────────────────────────────────────────────────────────────────────
# TAB 3: Extreme events
# ───────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Extreme climate events per year")

    col_a, col_b = st.columns(2)

    with col_a:
        heat_days = (
            filtered[filtered["T2M_MAX"] > 35]
            .groupby(["Country", "YEAR"])
            .size()
            .reset_index(name="extreme_heat_days")
            .groupby("Country")["extreme_heat_days"]
            .mean()
            .round(1)
            .sort_values()
        )
        fig, ax = plt.subplots()
        heat_days.plot(kind="bar", ax=ax, color="tomato")
        ax.set_title("Avg. extreme heat days/yr (T2M_MAX > 35°C)")
        ax.set_ylabel("Days")
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

    with col_b:
        def max_dry_run(series):
            is_dry = (series < 1).astype(int)
            max_run = run = 0
            for v in is_dry:
                run = run + 1 if v else 0
                max_run = max(max_run, run)
            return max_run

        dry_runs = (
            filtered.sort_values(["Country", "Date"])
            .groupby(["Country", "YEAR"])["PRECTOTCORR"]
            .apply(max_dry_run)
            .reset_index(name="max_dry_run")
            .groupby("Country")["max_dry_run"]
            .mean()
            .round(1)
            .sort_values()
        )
        fig, ax = plt.subplots()
        dry_runs.plot(kind="bar", ax=ax, color="goldenrod")
        ax.set_title("Avg. max consecutive dry days/yr")
        ax.set_ylabel("Days")
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

# ───────────────────────────────────────────────────────────────────────────────
# TAB 4: Vulnerability ranking
# ───────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Climate vulnerability ranking")
    st.caption(
        "Composite score: average rank across mean temperature, "
        "temp variability, precipitation variability, extreme heat days, "
        "and longest dry spell. Higher score = more vulnerable."
    )

    temp_s = (
        filtered.groupby("Country")["T2M"]
        .agg(mean_temp="mean", temp_std="std")
    )
    precip_s = filtered.groupby("Country")["PRECTOTCORR"].std().rename("precip_std")
    heat_s = (
        filtered[filtered["T2M_MAX"] > 35]
        .groupby(["Country", "YEAR"]).size()
        .reset_index(name="n")
        .groupby("Country")["n"].mean()
        .rename("heat_days")
    )
    dry_s = (
        filtered.sort_values(["Country", "Date"])
        .groupby(["Country", "YEAR"])["PRECTOTCORR"]
        .apply(max_dry_run)
        .reset_index(name="dry")
        .groupby("Country")["dry"].mean()
        .rename("dry_days")
    )

    vuln = pd.concat([temp_s, precip_s, heat_s, dry_s], axis=1).round(2)
    vuln["Vulnerability Score"] = vuln.rank().mean(axis=1).round(2)
    vuln = vuln.sort_values("Vulnerability Score", ascending=False)

    st.dataframe(vuln, use_container_width=True)

    # Heatmap of ranks
    fig, ax = plt.subplots(figsize=(10, 3))
    sns.heatmap(
        vuln.drop(columns="Vulnerability Score").T.rank(axis=1),
        annot=True, fmt=".0f",
        cmap="YlOrRd",
        ax=ax,
        cbar_kws={"label": "Rank (5 = most vulnerable)"},
    )
    ax.set_title("Vulnerability drivers (ranked)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    st.markdown("### 🌐 COP32 key observations")
    st.markdown("""
- **Fastest warming country**: Identify from the trend chart which country has the steepest upward slope — sustained warming accelerates drought frequency and crop failure risk.
- **Most unstable precipitation**: The country with the highest precipitation standard deviation faces the most unpredictable growing seasons, undermining food security.
- **Extreme heat and drought**: High heat-day counts combined with long dry spells indicate compounding climate stress — a key metric for loss-and-damage claims.
- **Ethiopia's profile**: Ethiopia sits at a moderate temperature baseline but shows strong seasonal variability and vulnerability to drought, which directly affects the ~80% of its population dependent on rain-fed agriculture.
- **Priority for climate finance**: The country scoring highest on the composite vulnerability index should be Ethiopia's primary case study when arguing for priority adaptation finance from the Global North at COP32.
    """)