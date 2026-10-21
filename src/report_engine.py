"""Proposal report generation engine for executive summaries and PDF/CSV deliverables.

Phase 6: Reusable content preparation and ReportLab PDF document assembly.
Separates data assembly from presentation rendering. Uses the existing
commercial, scenario, and risk engines as sources of truth.
Monetary values preserve Decimal precision and consistent currency formatting.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import io
import csv
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import xml.sax.saxutils

# ReportLab components
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
    HRFlowable,
)
from reportlab.pdfgen import canvas

from src.commercial_engine import (
    CENTS_QUANTIZE,
    PERCENT_QUANTIZE,
    CommercialInputs,
    CommercialResult,
    calculate_commercials,
    format_currency,
    format_percentage,
)
from src.scenario_engine import ScenarioComparison
from src.risk_engine import (
    RiskRecord,
    ChecklistItem,
    ReadinessResult,
    MitigationAction,
    FinancialStressCase,
    calculate_proposal_readiness,
    prioritize_risks,
    generate_mitigation_plan,
)


def _xml_escape(text: Optional[str]) -> str:
    """Safely escape text for inclusion in ReportLab Paragraph XML."""
    if text is None:
        return "Not provided"
    return xml.sax.saxutils.escape(str(text))


def generate_report_filename(title: str, client_name: str, ext: str = "pdf") -> str:
    """Generate a clean, filesystem-safe filename for proposal report artifacts."""
    clean_title = re.sub(r"[^\w\s-]", "", title or "Proposal").strip().lower()
    clean_title = re.sub(r"[-\s]+", "_", clean_title)[:30]

    clean_client = re.sub(r"[^\w\s-]", "", client_name or "Client").strip().lower()
    clean_client = re.sub(r"[-\s]+", "_", clean_client)[:20]

    date_tag = datetime.now().strftime("%Y%m%d")
    extension = ext.lstrip(".").lower()
    return f"dealwise_proposal_{clean_client}_{clean_title}_{date_tag}.{extension}"


@dataclass
class ProposalMetadata:
    """User-supplied context and descriptive terms for a consulting proposal."""

    title: str = "Commercial Proposal & Value Design Brief"
    client_name: str = "Hypothetical Enterprise Client"
    industry: str = "Data & Analytics Services"
    prepared_by: str = "Consulting Commercial Team"
    date_str: str = field(default_factory=lambda: datetime.now().strftime("%B %d, %Y"))
    business_problem: str = "Not provided"
    proposed_solution: str = "Not provided"
    scope_deliverables: str = "Not provided"
    assumptions_exclusions: str = "Not provided"
    timeline: str = "Not provided"
    payment_terms: str = "Not provided"
    notes_and_next_steps: str = "Not provided"
    is_hypothetical_demo: bool = True

    def validate(self) -> List[str]:
        """Validate metadata fields and return a list of incomplete field advisories."""
        warnings: List[str] = []
        if not self.title or not self.title.strip() or self.title.strip() == "Not provided":
            warnings.append("Proposal title is missing or blank.")
        if not self.client_name or not self.client_name.strip() or self.client_name.strip() == "Not provided":
            warnings.append("Client organization name is missing or blank.")
        if not self.business_problem or self.business_problem.strip() == "Not provided":
            warnings.append("Business problem definition is not provided.")
        if not self.proposed_solution or self.proposed_solution.strip() == "Not provided":
            warnings.append("Proposed solution description is not provided.")
        if not self.scope_deliverables or self.scope_deliverables.strip() == "Not provided":
            warnings.append("Scope and deliverables are not provided.")
        if not self.timeline or self.timeline.strip() == "Not provided":
            warnings.append("Delivery timeline is not provided.")
        if not self.payment_terms or self.payment_terms.strip() == "Not provided":
            warnings.append("Payment terms are not specified.")
        return warnings


@dataclass(frozen=True)
class CommercialScheduleData:
    """Structured commercial pricing schedule assembled from engine outputs."""

    currency: str
    base_quoted_price: Decimal
    discount_pct: Decimal
    net_revenue: Decimal
    delivery_labor_cost: Decimal
    software_tooling_cost: Decimal
    other_expenses: Decimal
    direct_estimated_cost: Decimal
    contingency_pct: Decimal
    contingency_amount: Decimal
    baseline_total_cost: Decimal
    cost_overrun_pct: Decimal
    scenario_total_cost: Decimal
    operating_profit: Decimal
    profit_margin_pct: Optional[Decimal]
    markup_pct: Optional[Decimal]
    target_margin_pct: Decimal
    meets_target_margin: bool
    break_even_net_revenue: Decimal
    required_quoted_price: Optional[Decimal]
    is_profitable: bool


@dataclass(frozen=True)
class ScenarioSummaryData:
    """Structured scenario comparison data for executive reporting."""

    baseline_revenue: Decimal
    scenario_revenue: Decimal
    delta_revenue: Decimal
    baseline_cost: Decimal
    scenario_cost: Decimal
    delta_cost: Decimal
    baseline_profit: Decimal
    scenario_profit: Decimal
    delta_profit: Decimal
    baseline_margin_pct: Optional[Decimal]
    scenario_margin_pct: Optional[Decimal]
    delta_margin_pp: Optional[Decimal]
    scenario_is_profitable: bool
    scenario_meets_target: bool


@dataclass(frozen=True)
class RiskSummaryData:
    """Structured risk and diligence readiness summary for executive reporting."""

    readiness_score_pct: Decimal
    completed_items_count: int
    applicable_items_count: int
    unresolved_items: List[ChecklistItem]
    prioritized_risks: List[RiskRecord]
    open_risks_count: int
    critical_risks_count: int
    high_risks_count: int
    mitigation_actions: List[MitigationAction]


@dataclass(frozen=True)
class ProposalReportContent:
    """Integrated, structured proposal report ready for PDF rendering and CSV export."""

    metadata: ProposalMetadata
    commercial: CommercialScheduleData
    scenario: Optional[ScenarioSummaryData]
    risk: RiskSummaryData
    generation_timestamp: str
    validation_warnings: List[str]
    disclaimer_text: str
    methodology_notes: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert structured report content to dictionary representation."""
        return {
            "title": self.metadata.title,
            "client_name": self.metadata.client_name,
            "industry": self.metadata.industry,
            "prepared_by": self.metadata.prepared_by,
            "date": self.metadata.date_str,
            "is_hypothetical_demo": self.metadata.is_hypothetical_demo,
            "net_revenue": float(self.commercial.net_revenue.quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP)),
            "scenario_total_cost": float(self.commercial.scenario_total_cost.quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP)),
            "operating_profit": float(self.commercial.operating_profit.quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP)),
            "profit_margin_pct": (
                float(self.commercial.profit_margin_pct.quantize(PERCENT_QUANTIZE, rounding=ROUND_HALF_UP))
                if self.commercial.profit_margin_pct is not None
                else None
            ),
            "meets_target_margin": self.commercial.meets_target_margin,
            "readiness_score_pct": float(self.risk.readiness_score_pct),
            "open_risks_count": self.risk.open_risks_count,
            "critical_risks_count": self.risk.critical_risks_count,
            "validation_warnings_count": len(self.validation_warnings),
        }


def assemble_commercial_schedule(
    inputs: CommercialInputs,
    result: CommercialResult,
    currency: str = "USD",
) -> CommercialScheduleData:
    """Extract and validate commercial pricing schedule from engine outputs."""
    inputs.validate()
    return CommercialScheduleData(
        currency=currency,
        base_quoted_price=inputs.base_quoted_price,
        discount_pct=inputs.discount_pct,
        net_revenue=result.net_revenue,
        delivery_labor_cost=inputs.delivery_costs,
        software_tooling_cost=inputs.software_tooling_costs,
        other_expenses=inputs.other_expenses,
        direct_estimated_cost=result.direct_estimated_cost,
        contingency_pct=inputs.contingency_pct,
        contingency_amount=result.contingency_amount,
        baseline_total_cost=result.baseline_total_cost,
        cost_overrun_pct=inputs.cost_overrun_pct,
        scenario_total_cost=result.scenario_total_cost,
        operating_profit=result.profit,
        profit_margin_pct=result.profit_margin_pct,
        markup_pct=result.markup_pct,
        target_margin_pct=inputs.target_margin_pct,
        meets_target_margin=result.meets_target_margin,
        break_even_net_revenue=result.break_even_net_revenue,
        required_quoted_price=result.required_quoted_price,
        is_profitable=result.profit > Decimal("0"),
    )


def assemble_scenario_summary(
    comparison: Optional[ScenarioComparison],
) -> Optional[ScenarioSummaryData]:
    """Convert an optional ScenarioComparison into structured summary data."""
    if comparison is None:
        return None

    return ScenarioSummaryData(
        baseline_revenue=comparison.baseline_result.net_revenue,
        scenario_revenue=comparison.scenario_result.net_revenue,
        delta_revenue=comparison.delta_net_revenue,
        baseline_cost=comparison.baseline_result.scenario_total_cost,
        scenario_cost=comparison.scenario_result.scenario_total_cost,
        delta_cost=comparison.delta_total_cost,
        baseline_profit=comparison.baseline_result.profit,
        scenario_profit=comparison.scenario_result.profit,
        delta_profit=comparison.delta_profit,
        baseline_margin_pct=comparison.baseline_result.profit_margin_pct,
        scenario_margin_pct=comparison.scenario_result.profit_margin_pct,
        delta_margin_pp=comparison.delta_margin_percentage_points,
        scenario_is_profitable=comparison.scenario_is_profitable,
        scenario_meets_target=comparison.scenario_meets_target,
    )


def assemble_risk_summary(
    risks: List[RiskRecord],
    checklist: List[ChecklistItem],
) -> RiskSummaryData:
    """Assemble prioritized risks, proposal readiness metrics, and mitigation actions."""
    readiness = calculate_proposal_readiness(checklist)
    sorted_risks = prioritize_risks(risks)
    plan = generate_mitigation_plan(risks)

    unresolved = [
        item for item in checklist if item.status.value in ("Not Started", "In Progress")
    ]
    open_count = sum(1 for r in risks if r.status.lower() in ("open", "in progress"))
    critical_count = sum(
        1 for r in risks if r.severity.value == "Critical" and r.status.lower() in ("open", "in progress")
    )
    high_count = sum(
        1 for r in risks if r.severity.value == "High" and r.status.lower() in ("open", "in progress")
    )

    return RiskSummaryData(
        readiness_score_pct=readiness.completion_pct,
        completed_items_count=readiness.completed_items,
        applicable_items_count=readiness.applicable_items,
        unresolved_items=unresolved,
        prioritized_risks=sorted_risks,
        open_risks_count=open_count,
        critical_risks_count=critical_count,
        high_risks_count=high_count,
        mitigation_actions=plan,
    )


def assemble_proposal_report(
    metadata: ProposalMetadata,
    commercial_inputs: CommercialInputs,
    commercial_result: CommercialResult,
    currency: str = "USD",
    scenario_comparison: Optional[ScenarioComparison] = None,
    risks: Optional[List[RiskRecord]] = None,
    checklist: Optional[List[ChecklistItem]] = None,
) -> ProposalReportContent:
    """Assemble complete proposal report content from underlying engine objects."""
    warnings = metadata.validate()
    comm_data = assemble_commercial_schedule(commercial_inputs, commercial_result, currency=currency)
    scen_data = assemble_scenario_summary(scenario_comparison)
    risk_data = assemble_risk_summary(risks or [], checklist or [])

    disclaimer = (
        "DEMONSTRATION & ADVISORY REPORT: This commercial briefing document is generated by "
        "DealWise for analytical structuring, margin sensitivity assessment, and pre-submission governance. "
        "All figures, staffing rate benchmarks, and risk scoring represent synthetic planning models. "
        "This document does not constitute an official Infosys contractual commitment, legal offer, or "
        "binding client agreement."
    )

    notes = (
        "Methodology: Direct delivery costs are modeled with Python Decimal precision. "
        "Contingency is calculated as a fixed reserve on direct costs. "
        "Risk scores reflect transparent ordinal evaluation (Likelihood x Impact, 1 to 25) "
        "and do not represent actuarial probabilities of default or calibrated monetary loss forecasts. "
        "Readiness scores indicate due diligence checklist completeness and do not replace partner sign-off."
    )

    return ProposalReportContent(
        metadata=metadata,
        commercial=comm_data,
        scenario=scen_data,
        risk=risk_data,
        generation_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        validation_warnings=warnings,
        disclaimer_text=disclaimer,
        methodology_notes=notes,
    )


# ---------------------------------------------------------------------------
# ReportLab Canvas with Running Headers & "Page X of Y" Footers
# ---------------------------------------------------------------------------

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas that tracks total pages and draws running headers and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        """Draw professional header and footer on every page except cover page (page 1)."""
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Top Header
        page_width, page_height = letter
        margin = 54  # 0.75 inch
        self.drawString(margin, page_height - 36, "DEALWISE — COMMERCIAL PROPOSAL & EXECUTIVE REPORT")
        self.drawRightString(page_width - margin, page_height - 36, "CONFIDENTIAL / ADVISORY USE ONLY")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(margin, page_height - 42, page_width - margin, page_height - 42)

        # Running Bottom Footer
        self.line(margin, 46, page_width - margin, 46)
        self.drawString(margin, 34, "Hypothetical Consulting Model • Data & Analytics Practice")
        self.drawRightString(page_width - margin, 34, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


# ---------------------------------------------------------------------------
# PDF Generation Function
# ---------------------------------------------------------------------------

def generate_proposal_pdf(content: ProposalReportContent) -> bytes:
    """Render a structured ProposalReportContent into an executive multi-page PDF document."""
    buffer = io.BytesIO()

    # Document Geometry: Letter size, 54pt margins (0.75 inch)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
        title=content.metadata.title,
        author="DealWise Commercial Engine",
    )

    # Styles
    base_styles = getSampleStyleSheet()

    # Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Navy
    c_secondary = colors.HexColor("#1E293B")  # Slate Navy
    c_accent = colors.HexColor("#2563EB")     # Corporate Blue
    c_muted = colors.HexColor("#64748B")      # Muted gray
    c_light_bg = colors.HexColor("#F8FAFC")   # Light gray fill
    c_border = colors.HexColor("#E2E8F0")     # Light border

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=base_styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=c_primary,
        alignment=0,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=c_accent,
        alignment=0,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=c_secondary,
        spaceAfter=6,
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_muted,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=c_secondary,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=c_primary,
    )

    table_cell_right = ParagraphStyle(
        "TableCellRight",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        alignment=2,
        textColor=c_secondary,
    )

    table_cell_right_bold = ParagraphStyle(
        "TableCellRightBold",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        alignment=2,
        textColor=c_primary,
    )

    story: List[Any] = []

    # -----------------------------------------------------------------------
    # COVER PAGE
    # -----------------------------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("DEALWISE COMMERCIAL PROPOSAL REPORT", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(_xml_escape(content.metadata.title), title_style))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=3, color=c_accent, spaceBefore=0, spaceAfter=20))

    meta_table_data = [
        [Paragraph("Target Client:", table_cell_bold), Paragraph(_xml_escape(content.metadata.client_name), table_cell_style)],
        [Paragraph("Target Industry:", table_cell_bold), Paragraph(_xml_escape(content.metadata.industry), table_cell_style)],
        [Paragraph("Prepared By:", table_cell_bold), Paragraph(_xml_escape(content.metadata.prepared_by), table_cell_style)],
        [Paragraph("Proposal Date:", table_cell_bold), Paragraph(_xml_escape(content.metadata.date_str), table_cell_style)],
        [Paragraph("Display Currency:", table_cell_bold), Paragraph(content.commercial.currency, table_cell_style)],
        [
            Paragraph("Proposal Readiness:", table_cell_bold),
            Paragraph(f"{content.risk.readiness_score_pct}% Diligence Checklist Complete", table_cell_bold),
        ],
        [
            Paragraph("Target Margin Alignment:", table_cell_bold),
            Paragraph(
                "Target Met" if content.commercial.meets_target_margin else "Target Margin Deficit",
                table_cell_bold,
            ),
        ],
    ]
    meta_table = Table(meta_table_data, colWidths=[150, 354])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light_bg),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 30))

    # Prominent Disclaimer Box on Cover Page
    disclaimer_p = Paragraph(
        f"<b>IMPORTANT COMMERCIAL NOTICE:</b> {_xml_escape(content.disclaimer_text)}",
        callout_style,
    )
    disclaimer_box = Table([[disclaimer_p]], colWidths=[504])
    disclaimer_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FCA5A5")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(disclaimer_box)

    if content.validation_warnings:
        story.append(Spacer(1, 15))
        warning_text = "<b>Diligence Incompleteness Warnings:</b><br/>" + "<br/>".join(
            f"• {_xml_escape(w)}" for w in content.validation_warnings
        )
        warn_box = Table([[Paragraph(warning_text, callout_style)]], colWidths=[504])
        warn_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FDE68A")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(warn_box)

    story.append(PageBreak())

    # -----------------------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY & STRATEGIC CONTEXT
    # -----------------------------------------------------------------------
    story.append(Paragraph("1.0 Executive Summary & Strategic Context", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=10))

    exec_summary_text = (
        f"This commercial proposal outlines the analytical value proposition, delivery economics, "
        f"and commercial structuring for <b>{_xml_escape(content.metadata.client_name)}</b> within the "
        f"<b>{_xml_escape(content.metadata.industry)}</b> sector. The proposed engagement reflects a baseline "
        f"quoted commitment of <b>{format_currency(content.commercial.base_quoted_price, content.commercial.currency)}</b>, "
        f"yielding a net realized revenue of <b>{format_currency(content.commercial.net_revenue, content.commercial.currency)}</b> "
        f"after accounting for client commercial concessions ({format_percentage(content.commercial.discount_pct * Decimal('100'))}). "
        f"Direct delivery costs and risk reserves total <b>{format_currency(content.commercial.scenario_total_cost, content.commercial.currency)}</b>, "
        f"generating a projected operating profit of <b>{format_currency(content.commercial.operating_profit, content.commercial.currency)}</b> "
        f"({format_percentage(content.commercial.profit_margin_pct) if content.commercial.profit_margin_pct is not None else 'N/A'} margin)."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>1.1 Business Problem Definition</b>", h2_style))
    story.append(Paragraph(_xml_escape(content.metadata.business_problem), body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.2 Proposed Value Design & Technical Solution</b>", h2_style))
    story.append(Paragraph(_xml_escape(content.metadata.proposed_solution), body_style))
    story.append(Spacer(1, 8))

    # -----------------------------------------------------------------------
    # SECTION 2: SCOPE, DELIVERABLES, ASSUMPTIONS & EXCLUSIONS
    # -----------------------------------------------------------------------
    story.append(Paragraph("2.0 Scope, Deliverables & Delivery Boundaries", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("<b>2.1 Core Delivery Scope & Key Milestones</b>", h2_style))
    story.append(Paragraph(_xml_escape(content.metadata.scope_deliverables), body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>2.2 Delivery Assumptions & Formal Exclusions</b>", h2_style))
    story.append(Paragraph(_xml_escape(content.metadata.assumptions_exclusions), body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>2.3 Proposed Timeline & Commercial Payment Milestones</b>", h2_style))
    time_terms_text = (
        f"<b>Delivery Timeline:</b> {_xml_escape(content.metadata.timeline)}<br/>"
        f"<b>Payment Terms:</b> {_xml_escape(content.metadata.payment_terms)}"
    )
    story.append(Paragraph(time_terms_text, body_style))
    story.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # SECTION 3: COMMERCIAL PRICING SCHEDULE & FINANCIAL METRICS
    # -----------------------------------------------------------------------
    story.append(Paragraph("3.0 Commercial Pricing Schedule & Financial Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=10))

    pricing_intro = (
        "All calculations are derived from the DealWise Decimal calculation engine. Figures represent "
        "reconciled planning estimates. No foreign exchange conversions are implied."
    )
    story.append(Paragraph(pricing_intro, body_style))
    story.append(Spacer(1, 6))

    comm = content.commercial
    curr = comm.currency

    price_rows = [
        [
            Paragraph("Commercial Element", table_header_style),
            Paragraph("Modeled Value", table_header_style),
            Paragraph("Analytical Notes", table_header_style),
        ],
        [
            Paragraph("Base Quoted Price (List)", table_cell_style),
            Paragraph(format_currency(comm.base_quoted_price, curr), table_cell_right_bold),
            Paragraph("Pre-discount contractual face value", table_cell_style),
        ],
        [
            Paragraph("Client Discount Concession", table_cell_style),
            Paragraph(format_percentage(comm.discount_pct * Decimal("100")), table_cell_right),
            Paragraph("Negotiated price concession percentage", table_cell_style),
        ],
        [
            Paragraph("Net Realized Revenue", table_cell_bold),
            Paragraph(format_currency(comm.net_revenue, curr), table_cell_right_bold),
            Paragraph("Base Quoted Price x (1 - Discount %)", table_cell_style),
        ],
        [
            Paragraph("Direct Delivery Labor Cost", table_cell_style),
            Paragraph(format_currency(comm.delivery_labor_cost, curr), table_cell_right),
            Paragraph("Base consulting delivery pyramid effort", table_cell_style),
        ],
        [
            Paragraph("Software, Cloud & Tooling", table_cell_style),
            Paragraph(format_currency(comm.software_tooling_cost, curr), table_cell_right),
            Paragraph("Direct third-party tooling & cloud expenses", table_cell_style),
        ],
        [
            Paragraph("Other Delivery Expenses", table_cell_style),
            Paragraph(format_currency(comm.other_expenses, curr), table_cell_right),
            Paragraph("Travel, onboarding, and administrative costs", table_cell_style),
        ],
        [
            Paragraph("Direct Estimated Cost", table_cell_bold),
            Paragraph(format_currency(comm.direct_estimated_cost, curr), table_cell_right_bold),
            Paragraph("Labor + Software + Expenses", table_cell_style),
        ],
        [
            Paragraph("Contingency Buffer Reserve", table_cell_style),
            Paragraph(
                f"{format_currency(comm.contingency_amount, curr)} ({format_percentage(comm.contingency_pct * Decimal('100'))})",
                table_cell_right,
            ),
            Paragraph("Contingency % applied to direct estimated cost", table_cell_style),
        ],
        [
            Paragraph("Baseline Total Estimated Cost", table_cell_bold),
            Paragraph(format_currency(comm.baseline_total_cost, curr), table_cell_right_bold),
            Paragraph("Direct Estimated Cost + Contingency Buffer", table_cell_style),
        ],
        [
            Paragraph("Labor Overrun Sensitivity Modeled", table_cell_style),
            Paragraph(format_percentage(comm.cost_overrun_pct * Decimal("100")), table_cell_right),
            Paragraph("Active scenario elongation assumption", table_cell_style),
        ],
        [
            Paragraph("Scenario Total Cost", table_cell_bold),
            Paragraph(format_currency(comm.scenario_total_cost, curr), table_cell_right_bold),
            Paragraph("Includes labor overrun impact", table_cell_style),
        ],
        [
            Paragraph("Projected Operating Profit / (Loss)", table_cell_bold),
            Paragraph(format_currency(comm.operating_profit, curr), table_cell_right_bold),
            Paragraph("Net Revenue - Scenario Total Cost", table_cell_style),
        ],
        [
            Paragraph("Profit Margin (%)", table_cell_bold),
            Paragraph(
                format_percentage(comm.profit_margin_pct) if comm.profit_margin_pct is not None else "N/A",
                table_cell_right_bold,
            ),
            Paragraph("Profit / Net Revenue (Practice target: " + format_percentage(comm.target_margin_pct * Decimal("100")) + ")", table_cell_style),
        ],
        [
            Paragraph("Markup on Cost (%)", table_cell_style),
            Paragraph(
                format_percentage(comm.markup_pct) if comm.markup_pct is not None else "N/A",
                table_cell_right,
            ),
            Paragraph("Profit / Scenario Total Cost", table_cell_style),
        ],
        [
            Paragraph("Break-Even Net Revenue", table_cell_style),
            Paragraph(format_currency(comm.break_even_net_revenue, curr), table_cell_right),
            Paragraph("Zero-profit revenue threshold", table_cell_style),
        ],
        [
            Paragraph("Required Quoted Price for Target Margin", table_cell_bold),
            Paragraph(
                format_currency(comm.required_quoted_price, curr) if comm.required_quoted_price is not None else "N/A",
                table_cell_right_bold,
            ),
            Paragraph("Price required to achieve target margin at active discount", table_cell_style),
        ],
    ]

    price_table = Table(price_rows, colWidths=[180, 120, 204], repeatRows=1)
    price_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
        ("BOX", (0, 0), (-1, -1), 1, c_secondary),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 3), (-1, 3), c_light_bg),
        ("BACKGROUND", (0, 7), (-1, 7), c_light_bg),
        ("BACKGROUND", (0, 9), (-1, 9), c_light_bg),
        ("BACKGROUND", (0, 11), (-1, 11), c_light_bg),
        ("BACKGROUND", (0, 12), (-1, 12), colors.HexColor("#EFF6FF") if comm.is_profitable else colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (0, 13), (-1, 13), colors.HexColor("#EFF6FF") if comm.meets_target_margin else colors.HexColor("#FFFBEB")),
    ]))
    story.append(price_table)
    story.append(Spacer(1, 14))

    # -----------------------------------------------------------------------
    # SECTION 4: WHAT-IF SCENARIO ANALYSIS (IF AVAILABLE)
    # -----------------------------------------------------------------------
    if content.scenario is not None:
        story.append(Paragraph("4.0 What-If Scenario Stress Comparison", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=10))

        scen = content.scenario
        scen_rows = [
            [
                Paragraph("Metric", table_header_style),
                Paragraph("Baseline Proposal", table_header_style),
                Paragraph("What-If Scenario", table_header_style),
                Paragraph("Variance (Delta)", table_header_style),
            ],
            [
                Paragraph("Net Realized Revenue", table_cell_style),
                Paragraph(format_currency(scen.baseline_revenue, curr), table_cell_right),
                Paragraph(format_currency(scen.scenario_revenue, curr), table_cell_right),
                Paragraph(format_currency(scen.delta_revenue, curr), table_cell_right_bold),
            ],
            [
                Paragraph("Total Estimated Cost", table_cell_style),
                Paragraph(format_currency(scen.baseline_cost, curr), table_cell_right),
                Paragraph(format_currency(scen.scenario_cost, curr), table_cell_right),
                Paragraph(format_currency(scen.delta_cost, curr), table_cell_right_bold),
            ],
            [
                Paragraph("Operating Profit", table_cell_style),
                Paragraph(format_currency(scen.baseline_profit, curr), table_cell_right),
                Paragraph(format_currency(scen.scenario_profit, curr), table_cell_right),
                Paragraph(format_currency(scen.delta_profit, curr), table_cell_right_bold),
            ],
            [
                Paragraph("Profit Margin (%)", table_cell_style),
                Paragraph(format_percentage(scen.baseline_margin_pct) if scen.baseline_margin_pct is not None else "N/A", table_cell_right),
                Paragraph(format_percentage(scen.scenario_margin_pct) if scen.scenario_margin_pct is not None else "N/A", table_cell_right),
                Paragraph(
                    (f"{scen.delta_margin_pp:+.2f} pp" if scen.delta_margin_pp is not None else "N/A"),
                    table_cell_right_bold,
                ),
            ],
        ]

        scen_table = Table(scen_rows, colWidths=[150, 118, 118, 118], repeatRows=1)
        scen_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BOX", (0, 0), (-1, -1), 1, c_secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 3), (-1, 3), c_light_bg),
        ]))
        story.append(scen_table)
        story.append(Spacer(1, 14))

    # -----------------------------------------------------------------------
    # SECTION 5: COMMERCIAL RISK REGISTER & MITIGATION ACTIONS
    # -----------------------------------------------------------------------
    sec_num = "5.0" if content.scenario is not None else "4.0"
    story.append(Paragraph(f"{sec_num} Commercial Risk Intelligence & Readiness Governance", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=10))

    readiness_summary = (
        f"<b>Proposal Readiness Score: {content.risk.readiness_score_pct}%</b> "
        f"({content.risk.completed_items_count} of {content.risk.applicable_items_count} applicable diligence items completed). "
        f"Total Active Risks: <b>{content.risk.open_risks_count}</b> "
        f"(Critical: <b>{content.risk.critical_risks_count}</b>, High: <b>{content.risk.high_risks_count}</b>)."
    )
    story.append(Paragraph(readiness_summary, body_style))
    story.append(Spacer(1, 6))

    if content.risk.prioritized_risks:
        story.append(Paragraph("<b>Top Commercial Risk Factors</b>", h2_style))
        risk_rows = [
            [
                Paragraph("Risk ID", table_header_style),
                Paragraph("Category", table_header_style),
                Paragraph("Description", table_header_style),
                Paragraph("Score", table_header_style),
                Paragraph("Severity", table_header_style),
                Paragraph("Owner", table_header_style),
            ]
        ]
        # Include up to top 6 risks to fit cleanly
        for r in content.risk.prioritized_risks[:6]:
            sev_color = colors.HexColor("#991B1B") if r.severity.value == "Critical" else (
                colors.HexColor("#B45309") if r.severity.value == "High" else colors.HexColor("#1E293B")
            )
            sev_style = ParagraphStyle(
                f"Sev_{r.risk_id}",
                parent=table_cell_bold,
                textColor=sev_color,
            )
            risk_rows.append([
                Paragraph(_xml_escape(r.risk_id), table_cell_bold),
                Paragraph(_xml_escape(r.category), table_cell_style),
                Paragraph(_xml_escape(r.description), table_cell_style),
                Paragraph(str(r.score), table_cell_right_bold),
                Paragraph(r.severity.value, sev_style),
                Paragraph(_xml_escape(r.owner), table_cell_style),
            ])

        risk_table = Table(risk_rows, colWidths=[64, 95, 185, 40, 55, 65], repeatRows=1)
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BOX", (0, 0), (-1, -1), 1, c_secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 8))

    if content.risk.mitigation_actions:
        story.append(Paragraph("<b>Prioritized Mitigation Action Plan</b>", h2_style))
        plan_rows = [
            [
                Paragraph("#", table_header_style),
                Paragraph("Action Required", table_header_style),
                Paragraph("Trigger / Category", table_header_style),
                Paragraph("Responsible Role", table_header_style),
            ]
        ]
        for m in content.risk.mitigation_actions[:5]:
            plan_rows.append([
                Paragraph(str(m.priority_rank), table_cell_bold),
                Paragraph(_xml_escape(m.action_text), table_cell_style),
                Paragraph(_xml_escape(m.trigger_rationale), table_cell_style),
                Paragraph(_xml_escape(m.suggested_role), table_cell_bold),
            ])

        plan_table = Table(plan_rows, colWidths=[24, 230, 150, 100], repeatRows=1)
        plan_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("BOX", (0, 0), (-1, -1), 1, c_secondary),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(plan_table)
        story.append(Spacer(1, 8))

    if content.risk.unresolved_items:
        story.append(Paragraph("<b>Outstanding Pre-Submission Diligence Items</b>", h2_style))
        unres_text = "<br/>".join(
            f"• <b>[{item.item_id}] {_xml_escape(item.title)}:</b> Status: {_xml_escape(item.status.value)}. {_xml_escape(item.description)}"
            for item in content.risk.unresolved_items[:5]
        )
        story.append(Paragraph(unres_text, body_style))
        story.append(Spacer(1, 10))

    # -----------------------------------------------------------------------
    # SECTION 6: NEXT STEPS & METHODOLOGICAL LIMITATIONS
    # -----------------------------------------------------------------------
    sec_num_next = "6.0" if content.scenario is not None else "5.0"
    story.append(Paragraph(f"{sec_num_next} Next Steps & Methodological Limitations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Commercial Next Steps</b>", h2_style))
    story.append(Paragraph(_xml_escape(content.metadata.notes_and_next_steps), body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Analytical Methodology & Limitations</b>", h2_style))
    story.append(Paragraph(_xml_escape(content.methodology_notes), callout_style))
    story.append(Spacer(1, 8))

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# CSV Export Functions for Proposals & Executive Briefs
# ---------------------------------------------------------------------------

def export_proposal_commercial_csv(content: ProposalReportContent) -> str:
    """Generate spreadsheet-compatible CSV export of commercial schedule and metrics."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["DEALWISE PROPOSAL COMMERCIAL BRIEF & PRICING SCHEDULE"])
    writer.writerow(["Proposal Title", content.metadata.title])
    writer.writerow(["Client Organization", content.metadata.client_name])
    writer.writerow(["Industry", content.metadata.industry])
    writer.writerow(["Prepared By", content.metadata.prepared_by])
    writer.writerow(["Date", content.metadata.date_str])
    writer.writerow(["Display Currency", content.commercial.currency])
    writer.writerow(["Hypothetical Model Disclaimer", content.disclaimer_text])
    writer.writerow([])

    def _c(val: Optional[Decimal]) -> str:
        if val is None:
            return "N/A"
        return str(val.quantize(CENTS_QUANTIZE, rounding=ROUND_HALF_UP))

    def _p(val: Optional[Decimal]) -> str:
        if val is None:
            return "N/A"
        return str(val.quantize(PERCENT_QUANTIZE, rounding=ROUND_HALF_UP))

    comm = content.commercial
    writer.writerow(["COMMERCIAL PRICING METRIC", "VALUE", "UNITS / NOTES"])
    writer.writerow(["Base Quoted Price", _c(comm.base_quoted_price), comm.currency])
    writer.writerow(["Discount Percentage", _p(comm.discount_pct * Decimal("100")), "%"])
    writer.writerow(["Net Realized Revenue", _c(comm.net_revenue), comm.currency])
    writer.writerow(["Direct Delivery Labor Cost", _c(comm.delivery_labor_cost), comm.currency])
    writer.writerow(["Software & Tooling Cost", _c(comm.software_tooling_cost), comm.currency])
    writer.writerow(["Other Delivery Expenses", _c(comm.other_expenses), comm.currency])
    writer.writerow(["Direct Estimated Cost", _c(comm.direct_estimated_cost), comm.currency])
    writer.writerow(["Contingency Percentage", _p(comm.contingency_pct * Decimal("100")), "%"])
    writer.writerow(["Contingency Buffer Amount", _c(comm.contingency_amount), comm.currency])
    writer.writerow(["Baseline Total Cost", _c(comm.baseline_total_cost), comm.currency])
    writer.writerow(["Cost Overrun Percentage", _p(comm.cost_overrun_pct * Decimal("100")), "%"])
    writer.writerow(["Scenario Total Cost", _c(comm.scenario_total_cost), comm.currency])
    writer.writerow(["Operating Profit / (Loss)", _c(comm.operating_profit), comm.currency])
    writer.writerow(["Profit Margin (%)", _p(comm.profit_margin_pct), "%"])
    writer.writerow(["Markup on Cost (%)", _p(comm.markup_pct), "%"])
    writer.writerow(["Target Margin (%)", _p(comm.target_margin_pct * Decimal("100")), "%"])
    writer.writerow(["Target Margin Met", "YES" if comm.meets_target_margin else "NO", "Governance Status"])
    writer.writerow(["Break-Even Revenue", _c(comm.break_even_net_revenue), comm.currency])
    writer.writerow(["Required Quoted Price for Target Margin", _c(comm.required_quoted_price), comm.currency])

    if content.scenario is not None:
        scen = content.scenario
        writer.writerow([])
        writer.writerow(["SCENARIO COMPARISON METRIC", "BASELINE", "SCENARIO", "DELTA"])
        writer.writerow(["Net Revenue", _c(scen.baseline_revenue), _c(scen.scenario_revenue), _c(scen.delta_revenue)])
        writer.writerow(["Total Cost", _c(scen.baseline_cost), _c(scen.scenario_cost), _c(scen.delta_cost)])
        writer.writerow(["Operating Profit", _c(scen.baseline_profit), _c(scen.scenario_profit), _c(scen.delta_profit)])
        writer.writerow([
            "Profit Margin (%)",
            _p(scen.baseline_margin_pct),
            _p(scen.scenario_margin_pct),
            _p(scen.delta_margin_pp),
        ])

    return output.getvalue()
