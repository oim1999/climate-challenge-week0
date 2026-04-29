# 🌍 EthioClimate COP32 Dashboard

A Streamlit dashboard for exploring historical climate data across five African countries (Ethiopia, Kenya, Sudan, Tanzania, Nigeria) in support of Ethiopia's COP32 preparations.

---

## Setup

**1. Clone the repo and create a virtual environment**
```bash
git clone https://github.com/your-username/climate-challenge-week0.git
cd climate-challenge-week0
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add data files**
Place the five cleaned CSVs in the `data/` folder:
data/
├── ethiopia_clean.csv
├── kenya_clean.csv
├── sudan_clean.csv
├── tanzania_clean.csv
└── nigeria_clean.csv

> The `data/` folder is git-ignored and never committed.

**4. Run the app**
```bash
streamlit run app/main.py
```
The app opens automatically at `http://localhost:8501`.

---

## Usage

Use the **sidebar** to filter the data:
- **Select countries** — choose one or more of the five countries
- **Year range** — zoom into a specific period
- **Climate variable** — switch between T2M, precipitation, humidity, wind speed, etc.

The dashboard has four tabs:

| Tab | What it shows |
|-----|--------------|
| 📈 Temperature trends | Monthly average line chart + summary stats |
| 🌧️ Precipitation | Boxplot distribution + summary stats |
| ⚡ Extreme events | Extreme heat days and longest dry spells per year |
| 📊 Vulnerability ranking | Composite ranking table + COP32 observations |


---

## Deployment

The app is deployed on Streamlit Community Cloud:
🔗 **[https://climate-challenge-week0-zq2jdgrpy9bdwkbotrfpdl.streamlit.app/](https://climate-challenge-week0-zq2jdgrpy9bdwkbotrfpdl.streamlit.app/)**

---