# DealWise Sample Data Architecture

This directory is designated for synthetic schemas, baseline benchmark files, and project delivery archetypes used by the DealWise platform.

## Commercial Governance & Data Integrity Notice
- **Zero Proprietary Data**: No real client data, proprietary consulting rate cards, or confidential contract agreements are stored in this repository.
- **Synthetic Models**: All data models in upcoming phases will use parameterized, normalized synthetic figures designed purely to illustrate value design methodologies, commercial waterfalls, and sensitivity analyses.

## Upcoming Schemas (Phase 2 & Phase 3)

### 1. Consulting Rate Cards (`sample_data/rate_cards.csv`)
Defines staffing tiers, normalized standard billing rates, cost baselines, and target utilization rates across role grades:
- `role_id`: Unique identifier (e.g., `EM-01`, `SA-02`, `DA-03`)
- `role_title`: Engagement Manager, Solutions Architect, Senior Data Engineer, Analytics Consultant, etc.
- `experience_tier`: Partner, Principal, Senior Manager, Senior Consultant, Consultant, Analyst
- `standard_billing_rate_usd_hr`: Benchmark catalog rate
- `target_utilization_pct`: Annualized target billable utilization
- `direct_labor_cost_usd_hr`: Normalized baseline cost (excluding overhead)

### 2. Engagement Archetypes (`sample_data/engagement_archetypes.json`)
Pre-configured delivery shapes for consulting solutions:
- `archetype_id`: e.g., `DATA_MODERNIZATION_12W`, `VALUE_AUDIT_6W`, `AI_GOVERNANCE_ROADMAP_8W`
- `duration_weeks`: Project timeline
- `pyramid_mix`: Distribution of roles across delivery phases
- `risk_weight_factor`: Base risk multiplier for delivery uncertainty

### 3. Contract Commercial Models (`sample_data/contract_models.json`)
Contract structure templates:
- `T_AND_M`: Pure Time & Materials with cap
- `FIXED_PRICE_PHASED`: Milestone-based fixed commercial agreement
- `RISK_REWARD_VALUE`: Hybrid base fee with margin upside tied to measurable analytics business outcomes
