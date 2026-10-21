# DealWise — Consulting Proposal & Commercial Intelligence Platform

**DealWise** is an analytical application designed for advisory and technology consulting leaders (specifically within Data & Analytics Value Design practices). It bridges technical scoping with commercial structuring, pricing governance, and margin sensitivity modeling for enterprise consulting proposals.

---

## 📌 Project Purpose

Consulting proposals frequently experience margin slippage and commercial vulnerability due to:
- Disconnected scoping between technical architects and commercial partners.
- Opaque staffing pyramid economics (imbalances in Partner-to-Analyst delivery leverage).
- Ineffective contract risk pricing (rigid Fixed Fee vs. un-capped Time & Materials).
- Lack of quantitative contingency modeling for scope volatility and delivery delays.

**DealWise** provides an integrated commercial workspace to model staffing economics, evaluate contract commercial structures, stress-test delivery margins, and produce partner-level governance audit summaries.

---

## 🚀 Current Phase 1 Capabilities

Phase 1 establishes the operational foundation and architectural blueprint for the platform:
- **Enterprise Application Shell**: Modular Streamlit application with custom corporate styling, clear visual hierarchy, and responsive layout.
- **Consulting Navigation Lifecycle**: Structured navigation reflecting the 5 advisory deal-shaping phases:
  1. *Overview & Architecture* (Operational)
  2. *Commercial Analysis* (Phase 2 Preview)
  3. *Scenario Simulator* (Phase 2 Preview)
  4. *Risk Review* (Phase 2 Preview)
  5. *Proposal Reports* (Phase 3 Preview)
- **Baseline Empty-State Dashboard**: Metric cards and structural waterfall charts illustrating planned commercial outputs without fabricated figures.
- **Data Governance & Transparency**: Built-in demonstration disclaimer confirming synthetic data policy with zero proprietary client data.
- **Automated Quality Testing**: Pytest suite validating configuration integrity, navigation schemas, disclaimer compliance, and core library availability.

*Note: In adherence to Phase 1 boundaries, financial formulas and interactive calculation logic are intentionally scheduled for Phase 2.*

---

## 🛠️ Technology Stack

- **Language**: Python 3.9+
- **Application Framework**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Interactive Visualizations**: [Plotly](https://plotly.com/python/)
- **Testing Framework**: [Pytest](https://docs.pytest.org/)
- **Version Control**: Git

Engineered to be lightweight, self-contained, and performant on macOS (optimized for 8 GB RAM systems with zero external database or cloud API requirements).

---

## 💻 Installation & Setup (macOS)

### 1. Prerequisites
Ensure Python 3.9 or newer is installed:
```bash
python3 --version
```

### 2. Clone or Navigate to Project
```bash
cd /path/to/dealwise
```

### 3. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Running the Application Locally

With your virtual environment activated:
```bash
streamlit run app.py
```

The application will be accessible at:
```
http://localhost:8501
```

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest -v
```

All 8 tests should pass, verifying metadata, compliance notices, navigation schemas, and module imports.

---

## 🗺️ Roadmap & Planned Future Phases

- [x] **Phase 1: Project Foundation** (Current)
  - Modular project structure, Git setup, Streamlit enterprise UI shell, automated test suite, data governance schema.
- [ ] **Phase 2: Commercial Modeling & Scenario Engine** (Upcoming)
  - Parameterized consulting rate cards (`sample_data/rate_cards.csv`).
  - Staffing pyramid leverage models and blended bill rate calculators.
  - Contract structuring trade-offs (Time & Materials vs. Capped T&M vs. Fixed Fee).
  - Scope contingency risk buffers and Margin-at-Risk (MaR) calculations.
- [ ] **Phase 3: Executive Governance & Reporting** (Upcoming)
  - Partner commercial briefing sheet generator.
  - Client-ready proposal fee schedules.
  - Commercial audit log exports (CSV/PDF summaries).

---

## 🛡️ License & Commercial Integrity

This project is built for portfolio and demonstration purposes. All figures, staffing rates, and contract models represent synthetic benchmarks. No proprietary client information or confidential pricing structures are included.
