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

## 🚀 Current Capabilities (Phases 1–4)

### Phase 1: Foundation & Enterprise UI Shell
- **Enterprise Application Shell**: Modular Streamlit application with custom corporate styling, clear visual hierarchy, and responsive layout.
- **Consulting Navigation Lifecycle**: Structured navigation reflecting deal-shaping phases:
  1. *Overview & Dashboard* (Operational)
  2. *Commercial Analysis* (Operational)
  3. *Scenario Simulator* (Operational)
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

### Phase 4: What-If Scenario Simulator
- **Independent Scenario Engine (`src/scenario_engine.py`)**:
  - **Baseline vs. Scenario Comparison**: Evaluates simulated client concessions, fee changes, labor overruns, and contingency adjustments side-by-side with the protected baseline.
  - **Delta Metrics Reconciliation**: Exact reconciliation where $\Delta \text{Profit} = \Delta \text{Revenue} - \Delta \text{Total Cost}$.
  - **Percentage-Point Margin Deltas**: Margin changes are mathematically expressed in **percentage points (pp)**, strictly preventing misleading relative percentage distortion.
  - **2D Sensitivity Matrix**: Generates multi-variable sensitivity grids across client discounts ($0\%-20\%$) and labor delivery overruns ($0\%-25\%$), visualized via an interactive Plotly heatmap with cell-level profit and margin inspection.
  - **Contracting Structure Evaluation (Fixed Fee vs. Time & Materials)**:
    - *Fixed Fee*: Firm absorbs 100% of delivery elongation risk; fee is locked and labor overruns directly erode profit margin.
    - *Time & Materials*: Client absorbs delivery volume variance; billable hours and labor cost rates are modeled separately, illustrating margin resilience under scope expansion.
  - **Audit CSV Export**: Built-in download functionality producing complete spreadsheet-compatible CSV audits containing baseline inputs, scenario deltas, and sensitivity grid tables.

### Phase 5: Commercial Risk Intelligence & Proposal Readiness
- **Independent Risk Engine (`src/risk_engine.py`)**:
  - **Risk Record Architecture**: Validated dataclasses supporting Risk ID, Category, Description, Likelihood (1–5), Impact (1–5), Calculated Risk Score (1–25), Configurable Severity Bands, Risk Owner, Mitigation Action, Status, and Optional Financial Exposure.
  - **Transparent Ordinal Scoring**: Uses explicit formula $\text{Score} = \text{Likelihood} \times \text{Impact}$ with four configurable bands: *Low* (1–4), *Moderate* (5–9), *High* (10–14), and *Critical* (15–25).
  - **Deterministic Proposal Readiness Checklist**: Tracks 9 core pre-bid diligence dimensions (scope definition, validated estimates, resource confirmation, commercial approval, acceptance criteria, payment terms, client dependencies, contract review). Quantified transparently as:
    $$\text{Readiness Score (\%)} = \frac{\text{Completed Items}}{\text{Applicable Items}} \times 100$$
  - **Automated Commercial Risk Identification**: Rule-based detection flags negative margins, target-margin shortfalls, aggressive client discounts ($\ge 15\%$), labor overruns without contingency coverage, and missing contract safeguards.
  - **Financial Exposure Stress Testing (No Double-Counting)**: Evaluates +20% labor overrun shock, +10% discount concession shock, and compound stress cases. Distinguishes standalone adverse stress outcomes from expected losses and explicitly tracks existing contingency inclusion to avoid double-counting.
  - **Prioritized Mitigation Engine**: Generates role-assigned, actionable advisory recommendations explaining triggering conditions and suggested mitigation playbooks.
  - **Integrated Risk Review UI & CSV Export**: Interactive Streamlit page allowing live risk register edits, checklist item updates, financial stress inspections, and downloadable CSV audits.

### Phase 6: Proposal and Executive Report Generator
- **Independent Report Engine (`src/report_engine.py`)**:
  - **Structured Data Assembly**: Decouples report data collection from visual rendering via `ProposalMetadata`, `CommercialScheduleData`, `ScenarioSummaryData`, `RiskSummaryData`, and `ProposalReportContent`.
  - **Strict Validation & Gap Flagging**: Validates proposal metadata without inventing facts; incomplete terms or missing scopes are surfaced as explicit diligence warnings rather than masked.
  - **Professional ReportLab PDF Generator**: Compiles multi-page executive PDFs directly in memory (`io.BytesIO`) using a custom two-pass `NumberedCanvas` (running headers, dynamic "Page X of Y" footers), clean corporate styling, and repeated table headers across pages (`repeatRows=1`).
  - **Reconciled Pricing & Scenario Schedules**: Directly leverages `CommercialResult` and `ScenarioComparison` as single sources of truth—guaranteeing 100% mathematical consistency across dashboard, register, and export artifacts.
  - **Interactive Proposal Reports Interface (`app.py`)**: Streamlit interface featuring a proposal narrative form, real-time completeness checks, synchronized KPI banner, multi-tab on-screen preview, and instant downloads.
  - **Tri-Format Commercial Exports**: One-click downloads for Executive Briefing PDF, Commercial Schedule CSV, and Risk/Diligence Governance CSV.

### Phase 7: End-to-End Quality Assurance & Deployment Readiness
- **Comprehensive Programmatic UI Testing**: Utilizes Streamlit's native `AppTest` framework to verify all 5 platform views, sidebar navigation, form inputs, and metric cards without throwing uncaught exceptions.
- **Cross-Engine Mathematical Reconciliation**: Verified that commercial engine outputs, scenario comparisons, financial stress tests, and PDF/CSV deliverables strictly reconcile without variance or double-counting.
- **Rapid Deployment Smoke Test (`tests/test_smoke.py`)**: Sub-second health check validating Python syntax, configuration schema, core Decimal calculation, and in-memory ReportLab PDF compilation.
- **Dependency & Security Hardening**: Tested fresh-environment installation from `requirements.txt`, verified zero hardcoded secrets or developer paths, and sanitized file export names.
- **Comprehensive Automated Test Suite**: 119 unit and integration tests executing cleanly with 100% pass rate.

### Phase 8 & Case Study Enhancement: Infosys-Aligned Enterprise Cloud & AI Transformation
- **Verified Public Facts & Official Data Provenance**: Integrates authoritative, verifiable public disclosures from official Infosys publications (Consulting Overview, Technology Transformation, Digital Platforms, Infosys Cobalt cloud suite, Infosys Topaz generative AI suite, and Integrated Annual Report corporate operating margin benchmarks of 20.3% - 21.0%).
- **Interactive Case Study Scenario Mode**: Toggle between the general-purpose workspace and the specialized enterprise case study preset (*"Hypothetical Enterprise Cloud & AI Transformation Proposal"*).
- **Staffing Pyramid & Delivery Economics**: Models a realistic 36-week, 4-phase transformation engagement featuring a 13-FTE delivery pyramid (Partner, Engagement Director, Principal Cloud Architects, Lead AI Engineers, Senior FinOps Consultants, and Analysts) with transparent leverage economics.
- **Commercial Calibration & Target Pricing**: Baseline parameters calibrated to a $1,250,000 quoted commitment, 5% commercial concession, 6.25% contingency reserve, 10% delivery labor overrun stress, and a 21.0% target margin matching corporate operating benchmarks.
- **Pre-configured Risk Register & Diligence Readiness**: Pre-loaded with 5 enterprise cloud/AI risks and a 9-item governance checklist reflecting practical advisory due diligence.
- **Executive Commercial Recommendation**: Provides structured contract structuring advisory (Hybrid Fixed-Fee core + Capped Time & Materials for AI workflow validation), concession ceilings, and automated FinOps consumption guardrails.
- **Upgraded PDF & CSV Artifacts**: Executive ReportLab PDF and CSV exports automatically incorporate provider reference details, executive recommendations, and a formal Verified Public Sources Bibliography.

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
13. **Scenario Variance Identity**:
    $$\Delta \text{Profit} = \Delta \text{Net Revenue} - \Delta \text{Total Cost}$$
14. **Margin Delta in Percentage Points**:
    $$\Delta \text{Margin (pp)} = \text{Scenario Margin (\%)} - \text{Baseline Margin (\%)} \quad (\text{not } \Delta \% / \%_{\text{base}})$$
15. **Ordinal Risk Score**:
    $$\text{Risk Score} = \text{Likelihood (1--5)} \times \text{Impact (1--5)}$$
    - Centrally defined score bands:
      - **Low**: Score 1–4
      - **Moderate**: Score 5–9
      - **High**: Score 10–14
      - **Critical**: Score 15–25
16. **Proposal Readiness Metric**:
    $$\text{Readiness Score (\%)} = \frac{\text{Completed Diligence Items}}{\text{Applicable Diligence Items}} \times 100 \quad (\text{excluding N/A items})$$

---

## 🛡️ Risk Intelligence & Exposure Methodology

### 1. Risk Scoring & Classification
- **Ordinal Scoring Formula**: Risk scores are evaluated as $\text{Likelihood} \times \text{Impact}$ on an integer grid from 1 to 25.
- **Categorization**: Risks span nine consulting deal dimensions: Scope Ambiguity, Unvalidated Estimates, Cost Overrun Risk, Aggressive Discounting, Resource Availability, Unclear Acceptance Criteria, Payment Term Uncertainty, Client Dependencies, and Contractual/Legal Governance.
- **Severity Bands**:
  - `Low` (1–4): Manageable via standard project management controls.
  - `Moderate` (5–9): Requires engagement manager attention and contingency tracking.
  - `High` (10–14): Requires commercial partner review, formal scope boundaries, or legal review.
  - `Critical` (15–25): Threatens deal viability; mandates executive sponsor sign-off or structural renegotiation before proposal submission.

### 2. Proposal Readiness Checklist Framework
- Evaluates 9 objective pre-submission commercial governance milestones.
- **Status Values**: `Not Started` (0% complete), `In Progress` (0% complete), `Complete` (100% complete), and `Not Applicable` (excluded from both numerator and denominator).
- **Governance Role**: Proposal readiness measures *operational diligence completeness*, not commercial deal approval. A 100% readiness score indicates all due diligence checks have been performed—it does not substitute for executive partner sign-off.

### 3. Financial Exposure & Stress-Case Methodology
- **Adverse Shock Scenarios**:
  - *Labor Overrun Shock (+20%)*: Simulates 20% delivery labor elongation under fixed-fee pricing.
  - *Discount Concession Shock (+10%)*: Simulates an additional 10 percentage point client price concession.
  - *Compound Commercial Shock*: Combines both labor overrun (+20%) and discount concession (+10%).
- **Reconciliation & Double-Counting Safeguard**: Stressed outcomes are calculated using the exact `calculate_commercials` engine. Each scenario states baseline profit/margin, stressed profit/margin, variance ($\Delta$), and explicitly reports whether contingency is already factored into direct costs. Hypothetical risk estimates are never added on top of a financial stress test that already models that specific overrun.
- **Deterministic Stress Case vs. Actuarial Expected Loss**: DealWise models explicit *deterministic stress scenarios* (what happens if an adverse shock occurs). It does not present these ordinal scores as statistically calibrated probabilities of default or actuarial expected loss forecasts.

### 4. Limitations of Rule-Based Risk Scoring
- **Qualitative Relative Ranking**: Ordinal multiplication ($L \times I$) ranks relative severity for human prioritization; it is not a continuous statistical metric.
- **Independence Assumption**: Risks are evaluated individually; correlation cascades (e.g., resource unavailability triggering delivery elongation which triggers client fee disputes) must be reviewed qualitatively by commercial leads.
- **Context Specificity**: Baseline risk flags are rule-generated heuristics from financial parameters; client relationship dynamics, strategic account value, and competitive bidding context require partner judgment.

---

## 📊 Worked Hypothetical Scenario Comparison

Consider a typical 10-week analytics engagement compared against a client concession scenario:

### Baseline Deal
- Base Price: \$100,000 | Discount: 5.0% | Delivery Labor: \$50,000 | Software/Expenses: \$10,000 | Contingency: 10.0% | Overrun: 0.0%
- **Net Revenue**: \$95,000.00
- **Total Cost**: \$66,000.00 (\$60,000 direct + \$6,000 contingency)
- **Profit**: \$29,000.00
- **Profit Margin**: **30.53%** (Target: 25.0%)

### What-If Scenario: Client Concession + Delivery Friction
- Negotiated Discount increases to **15.0%** (concession)
- Labor Delivery Overrun of **+20.0%** (2 weeks scope elongation)
- **Net Revenue**: $\$100,000 \times (1 - 0.15) = \mathbf{\$85,000.00}$ ($\Delta = -\$10,000.00$)
- **Scenario Delivery Cost**: $\$50,000 \times 1.20 = \mathbf{\$60,000.00}$
- **Scenario Total Cost**: $\$60,000 + \$10,000 + \$6,000 = \mathbf{\$76,000.00}$ ($\Delta = +\$10,000.00$)
- **Projected Profit**: $\$85,000 - \$76,000 = \mathbf{\$9,000.00}$ ($\Delta = -\$20,000.00$)
- **Profit Margin**: $\frac{\$9,000}{\$85,000} \times 100 = \mathbf{10.59\%}$
- **Margin Delta**: $10.59\% - 30.53\% = \mathbf{-19.94\text{ percentage points}}$
- **Target Margin Status**: Drops from **Target Met** (+5.53 pp buffer) to **Target Deficit** (-14.41 pp gap).

### Phase 5 Worked Example: Risk Intelligence & Proposal Readiness
Continuing with the baseline \$100,000 engagement:
- **Proposal Readiness Assessment**:
  - 7 items marked `Complete` (Scope, Estimates, Resources, Commercial Approvals, Payment Terms, Dependencies, Legal)
  - 1 item marked `In Progress` (Acceptance Criteria definition)
  - 1 item marked `Not Applicable` (Subcontractor audit)
  - **Readiness Score**: $\frac{7}{9 - 1} \times 100 = \mathbf{87.50\%}$ (Diligence indicates high completeness; pending final sign-off on acceptance criteria).
- **Risk Register Prioritization**:
  - `RSK-SCOPE-01`: Scope Ambiguity on Data Lake connectors. Likelihood = 4, Impact = 4 $\rightarrow \mathbf{\text{Risk Score } 16}$ (**Critical**). Action: Formalize written assumptions and out-of-scope boundaries. Assigned to: Engagement Director.
  - `RSK-ACCEPT-01`: Unclear acceptance sign-off criteria. Likelihood = 3, Impact = 3 $\rightarrow \mathbf{\text{Risk Score } 9}$ (**Moderate**). Action: Define measurable metric-based test conditions. Assigned to: Lead Architect.
- **Financial Exposure Stress Test**:
  - *Labor Overrun Shock (+20%)*: Delivery labor increases from \$50,000 to \$60,000. Total cost rises from \$66,000 to \$76,000. Operating profit falls from \$29,000 to \$19,000. Profit margin drops from 30.53% to 20.00% (-10.53 pp variance).
  - *Double-Counting Note*: The \$6,000 baseline contingency buffer remains modeled in direct costs; the +20% shock represents pure labor overrun without double-counting contingency provisions.
- **Automated Mitigation Action**:
  - Flagged: *Critical Risk Detected (RSK-SCOPE-01)* $\rightarrow$ Recommends locking change-control governance and testing labor sensitivity prior to commercial submission.

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

## 📄 Proposal Report Architecture & Governance Workflow

### 1. Architectural Pipeline
The report-generation module (`src/report_engine.py`) cleanly separates **data preparation** from **document rendering**:
```
User Scoping Inputs (Form)
        +
Commercial Calculation Engine (src/commercial_engine.py)
        +
Scenario Comparison Engine (src/scenario_engine.py)
        +
Risk Intelligence & Checklist Engine (src/risk_engine.py)
        │
        ▼
Structured Proposal Data Model (ProposalReportContent)
        │
        ├──► Executive Multi-Page PDF (ReportLab Platypus Engine)
        │       • Custom NumberedCanvas (running headers & dynamic "Page X of Y" footers)
        │       • Multi-level typography and corporate navy palette (#0F172A, #2563EB)
        │       • Auto-wrapping Paragraph tables with repeated headers across page breaks
        │       • Synthetic demo data disclaimers on cover & footer
        │
        ├──► Commercial Pricing Schedule CSV (Spreadsheet audit format)
        │
        └──► Risk & Diligence Governance CSV (Multi-section audit pack)
```

### 2. Multi-Page PDF Report Structure
The generated ReportLab PDF document adheres to consulting publication standards:
1. **Cover Page**: Proposal title, target client, industry, authoring team, date, currency, readiness score, and prominent synthetic data disclaimer.
2. **1.0 Executive Summary & Strategic Context**: Objective narrative synthesis, business problem definition, and proposed value design approach.
3. **2.0 Scope, Deliverables & Delivery Boundaries**: Key milestone breakdown, formal assumptions, and explicit out-of-scope exclusions.
4. **3.0 Commercial Pricing Schedule & Financial Architecture**: Full 17-line commercial table detailing list price, discount, net revenue, direct costs, contingency reserve, baseline total cost, overrun sensitivity, scenario total cost, operating profit/loss, margin %, markup %, break-even revenue, and required quoted price.
5. **4.0 What-If Scenario Stress Comparison** *(when scenario is evaluated)*: Baseline vs. what-if metrics with percentage-point margin deltas.
6. **5.0 Commercial Risk Intelligence & Readiness Governance**: Diligence readiness completion metric, unresolved checklist items, prioritized risk register table, and actionable mitigation plan.
7. **6.0 Next Steps & Methodological Limitations**: Immediate commercial actions and clear disclaimers regarding ordinal scoring and analytical modeling.

### 3. Commercial Commitments vs. Analytical Estimates
- **Demonstration & Advisory Status**: DealWise models analytical projections to guide commercial structuring and pre-submission diligence. It does **not** constitute an official Infosys contractual commitment, approved client proposal, or binding legal tender.
- **Human Approval Authority**: High readiness scores indicate thorough diligence completeness; they do not substitute for formal partner commercial sign-off and legal review.

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

All 119 unit and integration tests will execute, verifying:
- Application configuration, metadata, and disclaimer compliance.
- Commercial engine formulas, discounts, overruns, contingency, and target pricing.
- Margin versus markup mathematical distinction.
- Zero-revenue, zero-cost, and negative profit edge case handling.
- Input validation (rejection of negative costs, non-finite floats, out-of-range percentages).
- Executive dashboard KPI calculations and cost composition reconciliation.
- What-if scenario comparisons, percentage-point deltas, and profit identities.
- 2D sensitivity matrix dimensions and non-NaN values.
- Fixed Fee and Time & Materials contract model calculations.
- Risk engine scoring formulas, configurable severity band boundaries, and malformed record validation.
- Proposal readiness checklist score calculations, applicable denominators, and empty/full states.
- Rule-based mitigation plan generation and reason tracking.
- Financial stress cases with exact commercial engine reconciliation and double-counting safeguards.
- Report content assembly from valid inputs and graceful handling of missing fields.
- ReportLab in-memory PDF generation, valid byte streams, and text extraction via `pypdf`.
- Multi-page document resilience under long narrative content and extensive risk tables.
- Consistent currency labels without unintended foreign exchange conversion.
- CSV export format, headers, and numeric integrity for scenario audits, risk registers, and proposal schedules.
- Programmatic Streamlit UI execution across all 5 modules via `streamlit.testing.v1.AppTest`.
- Rapid deployment smoke test suite (`tests/test_smoke.py`) executing sub-second syntax and smoke health checks.
- Official Infosys public sources provenance, verified URLs, retrieval dates, and supported strategic claims (`tests/test_case_study.py`).
- Case study delivery pyramid structure, commercial calibration ($1.25M quoted, 21.0% margin), and risk registers.
- Dynamic case study mode toggle and two-way session-state synchronization in Streamlit `AppTest`.
- Case study PDF and CSV deliverable generation with embedded provider references and sources bibliography.

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

DealWise is architected to deploy directly to [Streamlit Community Cloud](https://streamlit.io/cloud) without requiring external databases, paid APIs, or local volume mounts:

### Deployment Steps
1. **Repository Setup**: Ensure the repository is hosted on GitHub.
2. **Streamlit Cloud Dashboard**: Select **New app**, choose the repository and `main` branch.
3. **App Entry Point**: Specify `app.py` as the main file path.
4. **Environment & Secrets**: No external environment variables or secrets are required (`secrets.toml` is not needed).
5. **Configuration**: Streamlit Community Cloud automatically reads `.streamlit/config.toml` (which enforces `headless = true`, `enableXsrfProtection = true`, and sets the custom corporate theme).
6. **In-Memory Operations**: Executive PDFs and CSVs are generated entirely in memory via Python `BytesIO` and `StringIO`, ensuring zero persistent disk writes on containerized infrastructure.

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
  - Reconciled Plotly visualizations for revenue/cost comparison and cost composition.
- [x] **Phase 4: What-If Scenario Simulator** (Complete)
  - Independent scenario comparison engine (`src/scenario_engine.py`).
  - Side-by-side delta metrics with percentage-point margin tracking.
  - Interactive Plotly 2D sensitivity heatmap (discount vs labor overrun).
  - Fixed Fee vs. Time & Materials contract risk allocation models.
  - Audit CSV export for spreadsheet analysis.
- [x] **Phase 5: Commercial Risk Intelligence & Proposal Readiness** (Complete)
  - Independent risk assessment and proposal readiness engine (`src/risk_engine.py`).
  - Ordinal scoring ($L \times I$) and centrally defined severity bands (Low, Moderate, High, Critical).
  - 9-dimension proposal readiness checklist with deterministic percentage score.
  - Financial exposure stress-testing (labor overrun shock, discount shock, compound shock) avoiding double counting.
  - Rule-based mitigation action generator with responsible consulting roles.
  - Risk register table, checklist UI, and downloadable risk assessment CSV export.
- [x] **Phase 6: Proposal and Executive Report Generator** (Complete)
  - Reusable report assembly engine (`src/report_engine.py`) and proposal metadata validation.
  - Multi-page executive ReportLab PDF generation with running headers and dynamic page numbering.
  - Proposal narrative form with real-time session persistence in Streamlit.
  - Multi-tab on-screen report preview (Pricing Schedule, Risk & Governance, Proposal Narrative).
  - Tri-format exports: Executive PDF, Commercial Schedule CSV, and Risk/Readiness Audit CSV.
- [x] **Phase 7: End-to-End Quality Assurance & Deployment Readiness** (Complete)
  - Full programmatic Streamlit UI integration test suite via `AppTest`.
  - Sub-second deployment smoke tests (`tests/test_smoke.py`).
  - Cross-module mathematical reconciliation and zero double-counting verification.
  - Fresh-environment installation verification from `requirements.txt`.
  - Security audit confirming zero secrets, no hardcoded developer paths, and safe HTML escaping.
- [x] **Phase 8: Production Release & GitHub Publication** (Complete)
  - Remote repository setup (`udaydomadiya08/dealwise`), release tagging (`v1.0.0`), and live deployment guide.

---

## 🛡️ License & Commercial Integrity
This project is an independent portfolio and professional demonstration project. It is not an official Infosys product, endorsement, or service offering. All figures, staffing models, pricing structures, and risk assessments represent synthetic demonstration benchmarks. No proprietary client information, confidential methodologies, or non-public commercial data are contained in this application.
