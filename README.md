# DealWise — Consulting Proposal & Commercial Intelligence Platform

**DealWise** is an analytical application designed for advisory and technology consulting leaders (specifically within Data & Analytics Value Design practices). It bridges technical scoping with commercial structuring, pricing governance, and margin sensitivity modeling for enterprise consulting proposals.

---

## 📌 Project Purpose

Consulting proposals frequently experience margin slippage and commercial vulnerability due to:
- Disconnected scoping between technical architects and commercial partners.
- Opaque staffing pyramid economics (imbalances in Partner-to-Analyst delivery leverage).
- Ineffective contract risk pricing (rigid Fixed Fee vs. un-capped Time & Materials).
- Lack of quantitative contingency modeling for scope volatility and delivery delays.

**DealWise** provides an integrated commercial workspace to model delivery economics, evaluate contract commercial structures, stress-test delivery margins, and calculate target-margin pricing.

---

## 🚀 Current Capabilities (Phases 1, 2 & 3)

### Phase 1: Foundation & Enterprise UI Shell
- **Enterprise Application Shell**: Modular Streamlit application with custom corporate styling, clear visual hierarchy, and responsive layout.
- **Consulting Navigation Lifecycle**: Structured navigation reflecting deal-shaping phases:
  1. *Overview & Dashboard* (Operational)
  2. *Commercial Analysis* (Operational)
  3. *Scenario Simulator* (Roadmap)
  4. *Risk Review* (Roadmap)
  5. *Proposal Reports* (Roadmap)
- **Data Governance & Transparency**: Built-in demonstration disclaimer confirming synthetic data policy with zero proprietary client data.

### Phase 2: Commercial Calculation Engine
- **Independent High-Precision Engine (`src/commercial_engine.py`)**:
  - Implemented with Python's `Decimal` type to avoid binary floating-point roundoff errors.
  - Strict input validation rejecting negative costs/prices, non-finite inputs, and invalid percentage bounds without silent clamping.
  - Zero-revenue and zero-cost handling (explicit `None` representation rather than `NaN` or `Inf`).
- **Interactive Commercial Analysis Interface**:
  - Real-time parameter inputs for quoted price, delivery labor, software/cloud tooling, expenses, contingency, client discount, delivery overrun, and practice target margin.
  - Dual-currency display support for **USD ($)** and **INR (₹)** (formatting display layer only; underlying math remains currency-neutral).
  - Commercial Health Advisories: Explicit alerts for negative margins (losses) and target-margin deficits.
  - Cost Component Breakdown table and Plotly bar visualizations.
  - Closed-form break-even revenue and target-margin required quoting calculator.

### Phase 3: Executive Analytics Dashboard
- **Executive Overview Dashboard (`app.py` & `src/dashboard.py`)**:
  - **Synchronized Session State**: Real-time two-way synchronization between the Executive Overview and Commercial Analysis pages. Modifications made on either view update the entire platform instantaneously without duplicating financial calculations.
  - **Executive KPI Cards**: Real-time display of Net Realized Revenue, Estimated Total Cost, Operating Profit/Loss (with accessible badges and text labels), Profit Margin, Practice Target Margin, and Break-Even Revenue (annotated with surplus/deficit).
  - **Commercial Health Assessment**: Objective, non-complacent advisory narrative explaining profit/loss standing, target-margin alignment, break-even distance, and explicit plain-language distinctions between profit margin and markup.
  - **Interactive Plotly Visualizations**:
    1. *Revenue vs. Delivery Cost & Operating Profit*: Compares net revenue and total cost with explicit profit/loss coloring and break-even reference line.
    2. *Cost Composition Breakdown*: Horizontal bar chart detailing base delivery, scenario labor overrun, software/cloud tooling, other expenses, and contingency buffer—strictly reconciled to the engine's total cost.
    3. *Profitability & Margin Benchmark*: Multi-rate benchmark comparing projected profit margin against practice target margin and markup on cost.
- **Comprehensive Automated Test Suite**: 45 passing unit tests covering platform metadata, navigation schemas, commercial math, edge cases, health interpretation, cost reconciliation, and Plotly figure generation.

---

## 📐 Financial Formulas & Definitions

The commercial engine executes the following exact formulas:

1. **Direct estimated cost**:
   $$\text{Direct Estimated Cost} = \text{Delivery Costs} + \text{Software/Tooling Costs} + \text{Other Expenses}$$
2. **Contingency amount**:
   $$\text{Contingency Amount} = \text{Direct Estimated Cost} \times \text{Contingency Percentage}$$
3. **Baseline total estimated cost**:
   $$\text{Baseline Total Cost} = \text{Direct Estimated Cost} + \text{Contingency Amount}$$
4. **Scenario delivery cost**:
   $$\text{Scenario Delivery Cost} = \text{Delivery Costs} \times (1 + \text{Cost Overrun Percentage})$$
5. **Scenario total estimated cost**:
   $$\text{Scenario Total Cost} = \text{Scenario Delivery Cost} + \text{Software/Tooling Costs} + \text{Other Expenses} + \text{Contingency Amount}$$
6. **Net revenue**:
   $$\text{Net Revenue} = \text{Base Quoted Price} \times (1 - \text{Discount Percentage})$$
7. **Profit**:
   $$\text{Profit} = \text{Net Revenue} - \text{Scenario Total Estimated Cost}$$
8. **Profit margin (%)**:
   $$\text{Profit Margin} = \frac{\text{Profit}}{\text{Net Revenue}} \times 100 \quad (\text{when Net Revenue} > 0)$$
9. **Markup (%)**:
   $$\text{Markup} = \frac{\text{Profit}}{\text{Scenario Total Estimated Cost}} \times 100 \quad (\text{when Scenario Total Cost} > 0)$$
10. **Break-even net revenue**:
    $$\text{Break-Even Net Revenue} = \text{Scenario Total Estimated Cost}$$
11. **Required net price for target margin**:
    $$\text{Required Net Price} = \frac{\text{Scenario Total Estimated Cost}}{1 - \text{Target Margin Percentage}} \quad (\text{where Target Margin} < 100\%)$$
12. **Required quoted price before discount**:
    $$\text{Required Quoted Price} = \frac{\text{Required Net Price}}{1 - \text{Discount Percentage}} \quad (\text{where Discount} < 100\%)$$

> **Core Distinction**: **Profit Margin** uses *Net Revenue* as the denominator (proportion of revenue converted to profit). **Markup** uses *Total Cost* as the denominator (percentage added on top of cost).

---

## 📊 Worked Hypothetical Example

Consider a typical 10-week enterprise analytics engagement:

### Inputs
- **Base Quoted Price**: \$100,000.00
- **Delivery Costs** (Labour & Subcontractors): \$50,000.00
- **Software, Cloud & Tooling Costs**: \$6,000.00
- **Other Project Expenses**: \$4,000.00
- **Contingency Percentage**: 10.0% ($0.10$)
- **Client Discount**: 5.0% ($0.05$)
- **Delivery-Cost Overrun**: 0.0% ($0.00$)
- **Practice Target Margin**: 25.0% ($0.25$)

### Step-by-Step Calculation
1. **Direct estimated cost** = $\$50,000 + \$6,000 + \$4,000 = \mathbf{\$60,000.00}$
2. **Contingency amount** = $\$60,000 \times 0.10 = \mathbf{\$6,000.00}$
3. **Baseline total estimated cost** = $\$60,000 + \$6,000 = \mathbf{\$66,000.00}$
4. **Scenario delivery cost** = $\$50,000 \times (1 + 0.00) = \mathbf{\$50,000.00}$
5. **Scenario total estimated cost** = $\$50,000 + \$6,000 + \$4,000 + \$6,000 = \mathbf{\$66,000.00}$
6. **Net revenue** = $\$100,000 \times (1 - 0.05) = \mathbf{\$95,000.00}$
7. **Profit** = $\$95,000 - \$66,000 = \mathbf{\$29,000.00}$
8. **Profit margin** = $\frac{\$29,000}{\$95,000} \times 100 = \mathbf{30.53\%}$ (exceeds $25.0\%$ target by $+5.53\%$)
9. **Markup** = $\frac{\$29,000}{\$66,000} \times 100 = \mathbf{43.94\%}$
10. **Break-even net revenue** = $\mathbf{\$66,000.00}$
11. **Required net price for 25% target margin** = $\frac{\$66,000}{1 - 0.25} = \frac{\$66,000}{0.75} = \mathbf{\$88,000.00}$
12. **Required quoted price before 5% discount** = $\frac{\$88,000}{1 - 0.05} = \frac{\$88,000}{0.95} = \mathbf{\$92,631.58}$

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

All 45 unit tests will execute, verifying:
- Application configuration, metadata, and disclaimer compliance.
- Normal and loss-making deal calculations.
- Discount, contingency, and cost-overrun effects.
- Margin versus markup mathematical distinction.
- Required target-margin pricing before and after discounts.
- Zero-revenue and zero-cost edge case handling.
- Input validation (rejection of negative costs, non-finite floats, out-of-range percentages).
- Boundary conditions (0% discount, 100% discount, 0% target margin).
- Currency and percentage formatting (USD and INR).
- Executive dashboard KPI calculations and cost composition reconciliation.
- Plotly chart datasets and loss/zero-state rendering.

---

## 🗺️ Roadmap & Planned Future Phases

- [x] **Phase 1: Project Foundation** (Complete)
  - Modular project structure, Git setup, Streamlit enterprise UI shell, data governance schema.
- [x] **Phase 2: Commercial Calculation Engine** (Complete)
  - Independent Decimal calculation engine (`src/commercial_engine.py`).
  - Interactive Commercial Analysis page in Streamlit with dual-currency display (USD/INR).
  - Closed-form break-even and target-margin required quoting solver.
- [x] **Phase 3: Executive Analytics Dashboard** (Complete)
  - Synchronized session state across Overview and Commercial Analysis.
  - Executive KPI cards with accessible health indicators and profit/loss labels.
  - Commercial Health diagnostic panel with margin vs markup analysis.
  - Interactive Plotly visualizations for revenue/cost comparison, reconciled cost composition, and margin benchmarks.
- [ ] **Phase 4: Contract Scenario Simulator & Governance Reporting** (Upcoming)
  - Contract structure comparison (Time & Materials vs. Capped T&M vs. Fixed Fee vs. Value-Linked).
  - Margin-at-Risk (MaR) sensitivity surfaces.
  - Partner commercial briefing sheet and client fee schedule exports.

---

## 🛡️ License & Commercial Integrity

This project is built for portfolio and demonstration purposes. All figures, staffing rates, and contract models represent synthetic benchmarks. No proprietary client information or confidential pricing structures are included.
