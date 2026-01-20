"""
Report Generation Module for Rinse Repeat Labs

Generates reports for:
- Ideas pipeline
- Tester program
- Project status
- Financial summaries
- Client reports
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.data_store import (
    get_ideas_store,
    get_testers_store,
    get_clients_store,
    get_projects_store,
    get_finances_store,
    IdeaStatus,
    TesterStatus,
    ProjectStatus,
    InvoiceStatus,
)
import config


REPORTS_DIR = config.BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def _save_report(name: str, content: str) -> Path:
    """Save a report to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}-{name}.md"
    path = REPORTS_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


# =============================================================================
# IDEAS REPORTS
# =============================================================================

def generate_ideas_pipeline_report() -> str:
    """Generate a report of the ideas pipeline."""
    store = get_ideas_store()
    all_ideas = store.get_all()

    # Group by status
    by_status = {}
    for idea in all_ideas:
        status = idea.get("status", "unknown")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(idea)

    lines = [
        "# Ideas Pipeline Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
    ]

    for status in IdeaStatus:
        count = len(by_status.get(status.value, []))
        lines.append(f"| {status.value.replace('_', ' ').title()} | {count} |")

    lines.append(f"| **Total** | **{len(all_ideas)}** |")
    lines.append("")

    # Pending review
    pending = by_status.get(IdeaStatus.SUBMITTED.value, [])
    if pending:
        lines.extend([
            "## Pending Review",
            "",
            "| ID | Name | Submitter | Submitted |",
            "|----|------|-----------|-----------|",
        ])
        for idea in pending:
            lines.append(
                f"| {idea['id']} | {idea['name']} | "
                f"{idea.get('submitter', {}).get('name', 'N/A')} | "
                f"{idea.get('created_at', '')[:10]} |"
            )
        lines.append("")

    # Under review
    under_review = by_status.get(IdeaStatus.UNDER_REVIEW.value, [])
    if under_review:
        lines.extend([
            "## Under Review",
            "",
            "| ID | Name | Platforms | Revenue Model |",
            "|----|------|-----------|---------------|",
        ])
        for idea in under_review:
            platforms = ", ".join(idea.get("platforms", []))
            lines.append(
                f"| {idea['id']} | {idea['name']} | {platforms} | "
                f"{idea.get('revenue_model', 'TBD')} |"
            )
        lines.append("")

    # Approved (ready for development)
    approved = by_status.get(IdeaStatus.APPROVED.value, [])
    if approved:
        lines.extend([
            "## Approved (Ready for Development)",
            "",
            "| ID | Name | Recommendation | Timeline |",
            "|----|------|----------------|----------|",
        ])
        for idea in approved:
            review = idea.get("review", {})
            lines.append(
                f"| {idea['id']} | {idea['name']} | "
                f"{review.get('recommendation', 'N/A')} | "
                f"{review.get('timeline_estimate', 'TBD')} |"
            )
        lines.append("")

    content = "\n".join(lines)
    _save_report("ideas-pipeline", content)
    return content


def generate_idea_detail_report(idea_id: str) -> str | None:
    """Generate a detailed report for a specific idea."""
    store = get_ideas_store()
    idea = store.get_by_id(idea_id)

    if not idea:
        return None

    submitter = idea.get("submitter", {})
    review = idea.get("review", {})

    lines = [
        f"# Idea Report: {idea.get('name', 'Untitled')}",
        f"**ID:** {idea['id']}",
        f"**Status:** {idea.get('status', 'unknown').replace('_', ' ').title()}",
        f"**Submitted:** {idea.get('created_at', '')[:10]}",
        "",
        "## Submitter",
        "",
        f"- **Name:** {submitter.get('name', 'N/A')}",
        f"- **Email:** {submitter.get('email', 'N/A')}",
        f"- **Company:** {submitter.get('company', 'N/A')}",
        "",
        "## Idea Details",
        "",
        f"**Description:**",
        idea.get("description", "No description provided."),
        "",
        f"**Platforms:** {', '.join(idea.get('platforms', ['Not specified']))}",
        f"**Revenue Model:** {idea.get('revenue_model', 'Not specified')}",
        f"**Timeline:** {idea.get('timeline', 'Not specified')}",
        f"**Budget Range:** {idea.get('budget_range', 'Not specified')}",
        "",
        "**Key Features:**",
    ]

    for feature in idea.get("features", ["None specified"]):
        lines.append(f"- {feature}")

    lines.extend([
        "",
        f"**Competitors:** {idea.get('competitors', 'Not specified')}",
        f"**Differentiation:** {idea.get('differentiation', 'Not specified')}",
        "",
    ])

    if review:
        lines.extend([
            "## Review Results",
            "",
            f"**Date:** {review.get('date', '')[:10]}",
            f"**Recommendation:** {review.get('recommendation', 'N/A')}",
            f"**Confidence:** {review.get('confidence', 'N/A')}",
            f"**Timeline Estimate:** {review.get('timeline_estimate', 'N/A')}",
            "",
            "**Concerns:**",
        ])
        for concern in review.get("concerns", ["None noted"]):
            lines.append(f"- {concern}")

        lines.extend([
            "",
            "**Next Steps:**",
        ])
        for step in review.get("next_steps", ["None specified"]):
            lines.append(f"- {step}")
        lines.append("")

    # Communication history
    comms = idea.get("communications", [])
    if comms:
        lines.extend([
            "## Communication History",
            "",
        ])
        for comm in comms:
            lines.extend([
                f"### {comm.get('subject', 'No subject')}",
                f"**Date:** {comm.get('timestamp', '')[:10]} | "
                f"**Direction:** {comm.get('direction', 'N/A')} | "
                f"**Channel:** {comm.get('channel', 'N/A')}",
                "",
                comm.get("content", ""),
                "",
            ])

    content = "\n".join(lines)
    _save_report(f"idea-{idea_id}", content)
    return content


# =============================================================================
# TESTER REPORTS
# =============================================================================

def generate_tester_program_report() -> str:
    """Generate a report of the tester program."""
    store = get_testers_store()
    all_testers = store.get_all()

    # Group by status
    by_status = {}
    for tester in all_testers:
        status = tester.get("status", "unknown")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(tester)

    # Device breakdown
    devices = {}
    for tester in all_testers:
        for device in tester.get("devices", []):
            device_type = device.get("type", "Unknown")
            devices[device_type] = devices.get(device_type, 0) + 1

    lines = [
        "# Tester Program Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        "### By Status",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]

    for status in TesterStatus:
        count = len(by_status.get(status.value, []))
        lines.append(f"| {status.value.replace('_', ' ').title()} | {count} |")

    lines.append(f"| **Total** | **{len(all_testers)}** |")
    lines.extend([
        "",
        "### By Device Type",
        "",
        "| Device | Testers |",
        "|--------|---------|",
    ])

    for device_type, count in sorted(devices.items(), key=lambda x: -x[1]):
        lines.append(f"| {device_type} | {count} |")

    lines.append("")

    # Active testers
    active = by_status.get(TesterStatus.ACTIVE.value, [])
    if active:
        lines.extend([
            "## Active Testers",
            "",
            "| Name | Devices | Projects | Rating | Earned |",
            "|------|---------|----------|--------|--------|",
        ])
        for tester in active:
            device_list = ", ".join(d.get("type", "") for d in tester.get("devices", []))
            rating = tester.get("rating", "N/A")
            if isinstance(rating, (int, float)):
                rating = f"{rating:.1f}/5"
            lines.append(
                f"| {tester['name']} | {device_list} | "
                f"{len(tester.get('projects', []))} | {rating} | "
                f"${tester.get('total_earned', 0):.2f} |"
            )
        lines.append("")

    # Pending applications
    pending = by_status.get(TesterStatus.APPLIED.value, [])
    if pending:
        lines.extend([
            "## Pending Applications",
            "",
            "| Name | Email | Devices | Experience | Applied |",
            "|------|-------|---------|------------|---------|",
        ])
        for tester in pending:
            device_list = ", ".join(d.get("type", "") for d in tester.get("devices", []))
            lines.append(
                f"| {tester['name']} | {tester['email']} | {device_list} | "
                f"{tester.get('experience_level', 'N/A')} | "
                f"{tester.get('created_at', '')[:10]} |"
            )
        lines.append("")

    content = "\n".join(lines)
    _save_report("tester-program", content)
    return content


# =============================================================================
# PROJECT REPORTS
# =============================================================================

def generate_projects_status_report() -> str:
    """Generate a status report for all projects."""
    store = get_projects_store()
    clients_store = get_clients_store()
    all_projects = store.get_all()

    # Group by status
    by_status = {}
    for project in all_projects:
        status = project.get("status", "unknown")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(project)

    lines = [
        "# Projects Status Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]

    for status in ProjectStatus:
        count = len(by_status.get(status.value, []))
        lines.append(f"| {status.value.replace('_', ' ').title()} | {count} |")

    lines.append(f"| **Total** | **{len(all_projects)}** |")
    lines.append("")

    # Active projects detail
    active_statuses = [
        ProjectStatus.PLANNING.value,
        ProjectStatus.DESIGN.value,
        ProjectStatus.DEVELOPMENT.value,
        ProjectStatus.QA.value,
        ProjectStatus.LAUNCH.value,
    ]

    active_projects = [p for p in all_projects if p.get("status") in active_statuses]

    if active_projects:
        lines.extend([
            "## Active Projects",
            "",
        ])

        for project in active_projects:
            client = clients_store.get_by_id(project.get("client_id", ""))
            client_name = client.get("company", "Unknown") if client else "Unknown"

            milestones = project.get("milestones", [])
            completed_milestones = sum(1 for m in milestones if m.get("completed"))
            next_milestone = next((m for m in milestones if not m.get("completed")), None)

            lines.extend([
                f"### {project['name']}",
                "",
                f"- **Client:** {client_name}",
                f"- **Status:** {project.get('status', 'N/A').replace('_', ' ').title()}",
                f"- **Platforms:** {', '.join(project.get('platforms', []))}",
                f"- **Target Launch:** {project.get('target_launch', 'TBD')}",
                f"- **Milestones:** {completed_milestones}/{len(milestones)} completed",
            ])

            if next_milestone:
                lines.append(f"- **Next Milestone:** {next_milestone.get('name', 'N/A')} (due: {next_milestone.get('due_date', 'TBD')})")

            lines.append("")

    content = "\n".join(lines)
    _save_report("projects-status", content)
    return content


# =============================================================================
# FINANCIAL REPORTS
# =============================================================================

def generate_financial_summary_report(period: str = "") -> str:
    """Generate a financial summary report.

    Args:
        period: Period to report on (e.g., "2026-01" for January 2026).
                If empty, reports on all time.
    """
    store = get_finances_store()
    clients_store = get_clients_store()
    all_records = store.get_all()

    if period:
        # Filter to period
        records = [r for r in all_records if r.get("created_at", "").startswith(period)]
        period_label = period
    else:
        records = all_records
        period_label = "All Time"

    # Categorize
    invoices = [r for r in records if r.get("type") == "invoice"]
    payments = [r for r in records if r.get("type") == "payment"]
    expenses = [r for r in records if r.get("type") == "expense"]
    revenue_shares = [r for r in records if r.get("type") == "revenue_share"]

    # Calculations
    total_invoiced = sum(i.get("amount", 0) for i in invoices)
    total_paid = sum(i.get("amount", 0) for i in invoices if i.get("status") == InvoiceStatus.PAID.value)
    total_outstanding = sum(i.get("amount", 0) for i in invoices
                          if i.get("status") in [InvoiceStatus.SENT.value, InvoiceStatus.OVERDUE.value])
    total_revenue_share = sum(r.get("our_share_amount", 0) for r in revenue_shares)
    total_expenses = sum(e.get("amount", 0) for e in expenses)

    total_revenue = total_paid + total_revenue_share
    net_income = total_revenue - total_expenses

    lines = [
        "# Financial Summary Report",
        f"**Period:** {period_label}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        "| Metric | Amount |",
        "|--------|--------|",
        f"| Total Invoiced | ${total_invoiced:,.2f} |",
        f"| Payments Received | ${total_paid:,.2f} |",
        f"| Outstanding | ${total_outstanding:,.2f} |",
        f"| Revenue Share Earned | ${total_revenue_share:,.2f} |",
        f"| **Total Revenue** | **${total_revenue:,.2f}** |",
        f"| Expenses | ${total_expenses:,.2f} |",
        f"| **Net Income** | **${net_income:,.2f}** |",
        "",
    ]

    # Outstanding invoices
    outstanding_invoices = [i for i in invoices
                          if i.get("status") in [InvoiceStatus.SENT.value, InvoiceStatus.OVERDUE.value]]
    if outstanding_invoices:
        lines.extend([
            "## Outstanding Invoices",
            "",
            "| Invoice # | Client | Amount | Due Date | Status |",
            "|-----------|--------|--------|----------|--------|",
        ])
        for inv in outstanding_invoices:
            client = clients_store.get_by_id(inv.get("client_id", ""))
            client_name = client.get("company", "Unknown") if client else "Unknown"
            lines.append(
                f"| {inv.get('invoice_number', 'N/A')} | {client_name} | "
                f"${inv.get('amount', 0):,.2f} | {inv.get('due_date', 'N/A')} | "
                f"{inv.get('status', 'N/A')} |"
            )
        lines.append("")

    # Revenue share breakdown
    if revenue_shares:
        lines.extend([
            "## Revenue Share Earnings",
            "",
            "| Project | Gross Revenue | Our Share % | Our Earnings |",
            "|---------|---------------|-------------|--------------|",
        ])
        for rs in revenue_shares:
            lines.append(
                f"| {rs.get('project_id', 'N/A')} | "
                f"${rs.get('gross_revenue', 0):,.2f} | "
                f"{rs.get('our_share_percent', 0)}% | "
                f"${rs.get('our_share_amount', 0):,.2f} |"
            )
        lines.append("")

    # Expenses breakdown
    if expenses:
        # Group by category
        by_category = {}
        for exp in expenses:
            cat = exp.get("category", "Other")
            by_category[cat] = by_category.get(cat, 0) + exp.get("amount", 0)

        lines.extend([
            "## Expenses by Category",
            "",
            "| Category | Amount |",
            "|----------|--------|",
        ])
        for cat, amount in sorted(by_category.items(), key=lambda x: -x[1]):
            lines.append(f"| {cat} | ${amount:,.2f} |")
        lines.append("")

    content = "\n".join(lines)
    _save_report(f"financial-summary-{period or 'all-time'}", content)
    return content


def generate_client_report(client_id: str) -> str | None:
    """Generate a detailed report for a specific client."""
    clients_store = get_clients_store()
    projects_store = get_projects_store()
    ideas_store = get_ideas_store()
    finances_store = get_finances_store()

    client = clients_store.get_by_id(client_id)
    if not client:
        return None

    # Get related records
    projects = [projects_store.get_by_id(pid) for pid in client.get("projects", [])]
    projects = [p for p in projects if p]  # Filter None

    ideas = [ideas_store.get_by_id(iid) for iid in client.get("ideas", [])]
    ideas = [i for i in ideas if i]

    invoices = finances_store.query(type="invoice", client_id=client_id)

    lines = [
        f"# Client Report: {client.get('company', 'Unknown')}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Contact Information",
        "",
        f"- **Name:** {client.get('name', 'N/A')}",
        f"- **Company:** {client.get('company', 'N/A')}",
        f"- **Email:** {client.get('email', 'N/A')}",
        f"- **Phone:** {client.get('phone', 'N/A')}",
        f"- **Primary Contact:** {client.get('primary_contact', 'N/A')}",
        f"- **Source:** {client.get('source', 'N/A')}",
        "",
        "## Financial Summary",
        "",
        f"- **Total Invoiced:** ${client.get('total_invoiced', 0):,.2f}",
        f"- **Total Paid:** ${client.get('total_paid', 0):,.2f}",
        f"- **Total Revenue:** ${client.get('total_revenue', 0):,.2f}",
        f"- **Outstanding:** ${client.get('total_invoiced', 0) - client.get('total_paid', 0):,.2f}",
        "",
    ]

    # Projects
    if projects:
        lines.extend([
            "## Projects",
            "",
            "| Name | Status | Revenue Model | Value |",
            "|------|--------|---------------|-------|",
        ])
        for project in projects:
            lines.append(
                f"| {project.get('name', 'N/A')} | "
                f"{project.get('status', 'N/A').replace('_', ' ').title()} | "
                f"{project.get('revenue_model', 'N/A')} | "
                f"${project.get('contract_value', 0):,.2f} |"
            )
        lines.append("")

    # Ideas
    if ideas:
        lines.extend([
            "## Ideas Submitted",
            "",
            "| Name | Status | Recommendation |",
            "|------|--------|----------------|",
        ])
        for idea in ideas:
            review = idea.get("review", {})
            lines.append(
                f"| {idea.get('name', 'N/A')} | "
                f"{idea.get('status', 'N/A').replace('_', ' ').title()} | "
                f"{review.get('recommendation', 'N/A')} |"
            )
        lines.append("")

    # Invoices
    if invoices:
        lines.extend([
            "## Invoice History",
            "",
            "| Invoice # | Amount | Status | Date |",
            "|-----------|--------|--------|------|",
        ])
        for inv in invoices:
            lines.append(
                f"| {inv.get('invoice_number', 'N/A')} | "
                f"${inv.get('amount', 0):,.2f} | "
                f"{inv.get('status', 'N/A')} | "
                f"{inv.get('created_at', '')[:10]} |"
            )
        lines.append("")

    content = "\n".join(lines)
    _save_report(f"client-{client_id}", content)
    return content
