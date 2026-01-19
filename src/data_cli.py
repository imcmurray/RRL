"""
Data Management CLI Commands for Rinse Repeat Labs

Provides CLI commands for managing:
- Ideas
- Testers
- Clients
- Projects
- Finances
- Reports
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.data_store import (
    get_ideas_store,
    get_testers_store,
    get_clients_store,
    get_projects_store,
    get_finances_store,
    get_agent_requests_store,
    IdeaStatus,
    TesterStatus,
    ProjectStatus,
    InvoiceStatus,
    PaymentType,
    FeatureRequestStatus,
    FeatureRequestPriority,
)
from src import reports

console = Console()


# =============================================================================
# IDEAS COMMANDS
# =============================================================================

@click.group()
def ideas():
    """Manage app idea submissions."""
    pass


@ideas.command("list")
@click.option("--status", "-s", type=click.Choice([s.value for s in IdeaStatus]), help="Filter by status")
@click.option("--limit", "-n", default=20, help="Number of ideas to show")
def ideas_list(status: str | None, limit: int):
    """List all ideas."""
    store = get_ideas_store()

    if status:
        ideas_data = store.query(status=status)
    else:
        ideas_data = store.get_all()

    ideas_data = ideas_data[:limit]

    if not ideas_data:
        console.print("[yellow]No ideas found.[/yellow]")
        return

    table = Table(title="Ideas")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Submitter")
    table.add_column("Status")
    table.add_column("Submitted")

    for idea in ideas_data:
        status_style = {
            "submitted": "yellow",
            "under_review": "blue",
            "approved": "green",
            "rejected": "red",
            "in_development": "cyan",
        }.get(idea.get("status", ""), "")

        table.add_row(
            idea["id"],
            idea.get("name", "Untitled")[:30],
            idea.get("submitter", {}).get("name", "N/A")[:20],
            f"[{status_style}]{idea.get('status', 'N/A')}[/{status_style}]",
            idea.get("created_at", "")[:10],
        )

    console.print(table)


@ideas.command("show")
@click.argument("idea_id")
def ideas_show(idea_id: str):
    """Show details for a specific idea."""
    store = get_ideas_store()
    idea = store.get_by_id(idea_id)

    if not idea:
        console.print(f"[red]Idea not found: {idea_id}[/red]")
        return

    submitter = idea.get("submitter", {})
    review = idea.get("review", {})

    console.print()
    console.print(Panel(f"[bold]{idea.get('name', 'Untitled')}[/bold]", border_style="cyan"))
    console.print()
    console.print(f"[bold]ID:[/bold] {idea['id']}")
    console.print(f"[bold]Status:[/bold] {idea.get('status', 'N/A')}")
    console.print(f"[bold]Submitted:[/bold] {idea.get('created_at', '')[:10]}")
    console.print()
    console.print("[bold]Submitter:[/bold]")
    console.print(f"  Name: {submitter.get('name', 'N/A')}")
    console.print(f"  Email: {submitter.get('email', 'N/A')}")
    console.print(f"  Company: {submitter.get('company', 'N/A')}")
    console.print()
    console.print("[bold]Description:[/bold]")
    console.print(idea.get("description", "No description"))
    console.print()
    console.print(f"[bold]Platforms:[/bold] {', '.join(idea.get('platforms', []))}")
    console.print(f"[bold]Revenue Model:[/bold] {idea.get('revenue_model', 'N/A')}")
    console.print(f"[bold]Timeline:[/bold] {idea.get('timeline', 'N/A')}")

    if review:
        console.print()
        console.print("[bold]Review:[/bold]")
        console.print(f"  Recommendation: {review.get('recommendation', 'N/A')}")
        console.print(f"  Confidence: {review.get('confidence', 'N/A')}")
        console.print(f"  Timeline Estimate: {review.get('timeline_estimate', 'N/A')}")


@ideas.command("add")
@click.option("--name", "-n", required=True, help="App name")
@click.option("--description", "-d", required=True, help="Description")
@click.option("--submitter-name", required=True, help="Submitter name")
@click.option("--submitter-email", required=True, help="Submitter email")
@click.option("--company", default="", help="Submitter company")
@click.option("--platforms", "-p", default="", help="Platforms (comma-separated)")
@click.option("--revenue-model", default="", help="Revenue model preference")
@click.option("--timeline", default="", help="Timeline expectations")
def ideas_add(name, description, submitter_name, submitter_email, company, platforms, revenue_model, timeline):
    """Add a new idea submission."""
    store = get_ideas_store()

    platforms_list = [p.strip() for p in platforms.split(",")] if platforms else []

    idea = store.create_idea(
        name=name,
        description=description,
        submitter_name=submitter_name,
        submitter_email=submitter_email,
        submitter_company=company,
        platforms=platforms_list,
        revenue_model=revenue_model,
        timeline=timeline,
    )

    console.print(f"[green]Created idea: {idea['id']} - {idea['name']}[/green]")


@ideas.command("status")
@click.argument("idea_id")
@click.argument("new_status", type=click.Choice([s.value for s in IdeaStatus]))
@click.option("--note", "-n", default="", help="Note about the status change")
def ideas_status(idea_id: str, new_status: str, note: str):
    """Update idea status."""
    store = get_ideas_store()
    result = store.update_status(idea_id, IdeaStatus(new_status), note)

    if result:
        console.print(f"[green]Updated idea {idea_id} status to: {new_status}[/green]")
    else:
        console.print(f"[red]Idea not found: {idea_id}[/red]")


@ideas.command("report")
@click.option("--id", "idea_id", help="Generate report for specific idea")
def ideas_report(idea_id: str | None):
    """Generate ideas report."""
    if idea_id:
        report = reports.generate_idea_detail_report(idea_id)
        if report:
            console.print(report)
        else:
            console.print(f"[red]Idea not found: {idea_id}[/red]")
    else:
        report = reports.generate_ideas_pipeline_report()
        console.print(report)


# =============================================================================
# TESTERS COMMANDS
# =============================================================================

@click.group()
def testers():
    """Manage beta tester program."""
    pass


@testers.command("list")
@click.option("--status", "-s", type=click.Choice([s.value for s in TesterStatus]), help="Filter by status")
@click.option("--device", "-d", help="Filter by device type")
def testers_list(status: str | None, device: str | None):
    """List all testers."""
    store = get_testers_store()

    if device:
        testers_data = store.get_by_device_type(device)
    elif status:
        testers_data = store.query(status=status)
    else:
        testers_data = store.get_all()

    if not testers_data:
        console.print("[yellow]No testers found.[/yellow]")
        return

    table = Table(title="Testers")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Devices")
    table.add_column("Status")
    table.add_column("Rating")

    for tester in testers_data:
        devices = ", ".join(d.get("type", "") for d in tester.get("devices", []))
        rating = tester.get("rating")
        rating_str = f"{rating:.1f}/5" if rating else "N/A"

        table.add_row(
            tester["id"],
            tester.get("name", "N/A"),
            tester.get("email", "N/A"),
            devices[:25],
            tester.get("status", "N/A"),
            rating_str,
        )

    console.print(table)


@testers.command("add")
@click.option("--name", "-n", required=True, help="Tester name")
@click.option("--email", "-e", required=True, help="Tester email")
@click.option("--devices", "-d", required=True, help="Devices (format: 'iPhone:14 Pro:iOS 17,Android:Pixel 7:Android 14')")
@click.option("--experience", type=click.Choice(["new", "some", "experienced", "professional"]), default="some")
@click.option("--hours", type=int, default=5, help="Hours per week available")
@click.option("--payment-method", type=click.Choice(["paypal", "venmo", "crypto"]), default="paypal")
@click.option("--payment-details", required=True, help="Payment email or wallet address")
def testers_add(name, email, devices, experience, hours, payment_method, payment_details):
    """Add a new tester application."""
    store = get_testers_store()

    # Parse devices
    devices_list = []
    for d in devices.split(","):
        parts = d.strip().split(":")
        if len(parts) >= 2:
            devices_list.append({
                "type": parts[0],
                "model": parts[1] if len(parts) > 1 else "",
                "os": parts[2] if len(parts) > 2 else "",
            })

    tester = store.create_tester(
        name=name,
        email=email,
        devices=devices_list,
        experience_level=experience,
        hours_per_week=hours,
        payment_method=payment_method,
        payment_details=payment_details,
    )

    console.print(f"[green]Created tester: {tester['id']} - {tester['name']}[/green]")


@testers.command("approve")
@click.argument("tester_id")
@click.option("--note", "-n", default="", help="Approval note")
def testers_approve(tester_id: str, note: str):
    """Approve a tester application."""
    store = get_testers_store()
    result = store.approve(tester_id, note)

    if result:
        console.print(f"[green]Approved tester: {tester_id}[/green]")
    else:
        console.print(f"[red]Tester not found: {tester_id}[/red]")


@testers.command("reject")
@click.argument("tester_id")
@click.option("--reason", "-r", required=True, help="Rejection reason")
def testers_reject(tester_id: str, reason: str):
    """Reject a tester application."""
    store = get_testers_store()
    result = store.reject(tester_id, reason)

    if result:
        console.print(f"[yellow]Rejected tester: {tester_id}[/yellow]")
    else:
        console.print(f"[red]Tester not found: {tester_id}[/red]")


@testers.command("assign")
@click.argument("tester_id")
@click.argument("project_id")
def testers_assign(tester_id: str, project_id: str):
    """Assign a tester to a project."""
    testers_store = get_testers_store()
    projects_store = get_projects_store()

    result = testers_store.assign_to_project(tester_id, project_id)
    if result:
        projects_store.assign_tester(project_id, tester_id)
        console.print(f"[green]Assigned tester {tester_id} to project {project_id}[/green]")
    else:
        console.print(f"[red]Tester not found: {tester_id}[/red]")


@testers.command("report")
def testers_report():
    """Generate tester program report."""
    report = reports.generate_tester_program_report()
    console.print(report)


# =============================================================================
# CLIENTS COMMANDS
# =============================================================================

@click.group()
def clients():
    """Manage client relationships."""
    pass


@clients.command("list")
def clients_list():
    """List all clients."""
    store = get_clients_store()
    clients_data = store.get_all()

    if not clients_data:
        console.print("[yellow]No clients found.[/yellow]")
        return

    table = Table(title="Clients")
    table.add_column("ID", style="dim")
    table.add_column("Company")
    table.add_column("Contact")
    table.add_column("Projects")
    table.add_column("Total Revenue")

    for client in clients_data:
        table.add_row(
            client["id"],
            client.get("company", "N/A"),
            client.get("name", "N/A"),
            str(len(client.get("projects", []))),
            f"${client.get('total_revenue', 0):,.2f}",
        )

    console.print(table)


@clients.command("add")
@click.option("--name", "-n", required=True, help="Contact name")
@click.option("--company", "-c", required=True, help="Company name")
@click.option("--email", "-e", required=True, help="Email address")
@click.option("--phone", default="", help="Phone number")
@click.option("--source", default="", help="How they found us")
def clients_add(name, company, email, phone, source):
    """Add a new client."""
    store = get_clients_store()

    client = store.create_client(
        name=name,
        company=company,
        email=email,
        phone=phone,
        source=source,
    )

    console.print(f"[green]Created client: {client['id']} - {client['company']}[/green]")


@clients.command("show")
@click.argument("client_id")
def clients_show(client_id: str):
    """Show client details."""
    store = get_clients_store()
    client = store.get_by_id(client_id)

    if not client:
        console.print(f"[red]Client not found: {client_id}[/red]")
        return

    console.print()
    console.print(Panel(f"[bold]{client.get('company', 'Unknown')}[/bold]", border_style="cyan"))
    console.print()
    console.print(f"[bold]ID:[/bold] {client['id']}")
    console.print(f"[bold]Contact:[/bold] {client.get('name', 'N/A')}")
    console.print(f"[bold]Email:[/bold] {client.get('email', 'N/A')}")
    console.print(f"[bold]Phone:[/bold] {client.get('phone', 'N/A')}")
    console.print()
    console.print(f"[bold]Projects:[/bold] {len(client.get('projects', []))}")
    console.print(f"[bold]Total Revenue:[/bold] ${client.get('total_revenue', 0):,.2f}")
    console.print(f"[bold]Outstanding:[/bold] ${client.get('total_invoiced', 0) - client.get('total_paid', 0):,.2f}")


@clients.command("report")
@click.argument("client_id")
def clients_report(client_id: str):
    """Generate client report."""
    report = reports.generate_client_report(client_id)
    if report:
        console.print(report)
    else:
        console.print(f"[red]Client not found: {client_id}[/red]")


# =============================================================================
# PROJECTS COMMANDS
# =============================================================================

@click.group()
def projects():
    """Manage development projects."""
    pass


@projects.command("list")
@click.option("--status", "-s", type=click.Choice([s.value for s in ProjectStatus]), help="Filter by status")
@click.option("--active", "-a", is_flag=True, help="Show only active projects")
def projects_list(status: str | None, active: bool):
    """List all projects."""
    store = get_projects_store()

    if active:
        projects_data = store.get_active()
    elif status:
        projects_data = store.query(status=status)
    else:
        projects_data = store.get_all()

    if not projects_data:
        console.print("[yellow]No projects found.[/yellow]")
        return

    table = Table(title="Projects")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Target Launch")
    table.add_column("Value")

    for project in projects_data:
        status_style = {
            "planning": "yellow",
            "design": "blue",
            "development": "cyan",
            "qa": "magenta",
            "launch": "green",
            "maintenance": "dim",
        }.get(project.get("status", ""), "")

        table.add_row(
            project["id"],
            project.get("name", "N/A")[:25],
            f"[{status_style}]{project.get('status', 'N/A')}[/{status_style}]",
            project.get("target_launch", "TBD"),
            f"${project.get('contract_value', 0):,.2f}",
        )

    console.print(table)


@projects.command("report")
def projects_report():
    """Generate projects status report."""
    report = reports.generate_projects_status_report()
    console.print(report)


# =============================================================================
# FINANCES COMMANDS
# =============================================================================

@click.group()
def finances():
    """Manage financial data."""
    pass


@finances.command("invoices")
@click.option("--status", "-s", type=click.Choice([s.value for s in InvoiceStatus]), help="Filter by status")
def finances_invoices(status: str | None):
    """List invoices."""
    store = get_finances_store()

    if status:
        invoices = store.get_invoices(InvoiceStatus(status))
    else:
        invoices = store.get_invoices()

    if not invoices:
        console.print("[yellow]No invoices found.[/yellow]")
        return

    table = Table(title="Invoices")
    table.add_column("Invoice #")
    table.add_column("Client")
    table.add_column("Amount")
    table.add_column("Due Date")
    table.add_column("Status")

    clients_store = get_clients_store()

    for inv in invoices:
        client = clients_store.get_by_id(inv.get("client_id", ""))
        client_name = client.get("company", "Unknown") if client else "Unknown"

        table.add_row(
            inv.get("invoice_number", "N/A"),
            client_name[:20],
            f"${inv.get('amount', 0):,.2f}",
            inv.get("due_date", "N/A"),
            inv.get("status", "N/A"),
        )

    console.print(table)


@finances.command("create-invoice")
@click.option("--client", "-c", required=True, help="Client ID")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--amount", "-a", required=True, type=float, help="Invoice amount")
@click.option("--description", "-d", required=True, help="Description")
@click.option("--due-date", required=True, help="Due date (YYYY-MM-DD)")
def finances_create_invoice(client, project, amount, description, due_date):
    """Create a new invoice."""
    store = get_finances_store()

    invoice = store.create_invoice(
        client_id=client,
        project_id=project,
        amount=amount,
        description=description,
        due_date=due_date,
    )

    console.print(f"[green]Created invoice: {invoice.get('invoice_number')}[/green]")


@finances.command("report")
@click.option("--period", "-p", default="", help="Period (YYYY-MM)")
def finances_report(period: str):
    """Generate financial summary report."""
    report = reports.generate_financial_summary_report(period)
    console.print(report)


# =============================================================================
# REPORTS COMMAND
# =============================================================================

@click.group()
def report():
    """Generate various reports."""
    pass


@report.command("all")
def report_all():
    """Generate all reports."""
    console.print("[bold]Generating all reports...[/bold]")
    console.print()

    console.print("Ideas Pipeline Report:")
    reports.generate_ideas_pipeline_report()
    console.print("[green]  ✓ Saved to reports/[/green]")

    console.print("Tester Program Report:")
    reports.generate_tester_program_report()
    console.print("[green]  ✓ Saved to reports/[/green]")

    console.print("Projects Status Report:")
    reports.generate_projects_status_report()
    console.print("[green]  ✓ Saved to reports/[/green]")

    console.print("Financial Summary Report:")
    reports.generate_financial_summary_report()
    console.print("[green]  ✓ Saved to reports/[/green]")

    console.print()
    console.print("[bold green]All reports generated successfully![/bold green]")


# =============================================================================
# AGENT REQUESTS COMMANDS
# =============================================================================

# Agent display names
AGENT_NAMES = {
    "ceo": "CEO",
    "cfo": "CFO",
    "cito": "CITO",
    "sales": "Sales",
    "legal": "Legal",
    "dev_lead": "DevLead",
    "design_lead": "DesignLead",
    "qa_lead": "QALead",
    "pm": "PM",
    "customer_success": "CustomerSuccess",
    "marketing": "Marketing",
    "support": "Support",
}


@click.group()
def requests():
    """Manage agent feature requests."""
    pass


@requests.command("list")
@click.option("--agent", "-a", type=click.Choice(list(AGENT_NAMES.keys())), help="Filter by agent")
@click.option("--status", "-s", type=click.Choice([s.value for s in FeatureRequestStatus]), help="Filter by status")
@click.option("--limit", "-n", default=20, help="Number of requests to show")
def requests_list(agent: str | None, status: str | None, limit: int):
    """List agent feature requests."""
    store = get_agent_requests_store()

    if agent:
        requests_data = store.get_by_agent(agent)
    elif status:
        requests_data = store.get_by_status(FeatureRequestStatus(status))
    else:
        requests_data = store.get_all()

    requests_data = requests_data[:limit]

    if not requests_data:
        console.print("[yellow]No requests found.[/yellow]")
        return

    table = Table(title="Agent Feature Requests")
    table.add_column("ID", style="dim")
    table.add_column("Agent")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Created")

    for req in requests_data:
        priority_style = {
            "critical": "red bold",
            "high": "yellow",
            "medium": "blue",
            "low": "dim",
        }.get(req.get("priority", "medium"), "")

        status_style = {
            "submitted": "yellow",
            "under_review": "blue",
            "approved": "green",
            "rejected": "red",
            "in_progress": "cyan",
            "implemented": "green bold",
            "deferred": "dim",
        }.get(req.get("status", ""), "")

        table.add_row(
            req["id"][:8],
            AGENT_NAMES.get(req.get("agent_id", ""), req.get("agent_id", "N/A")),
            req.get("title", "Untitled")[:30],
            req.get("request_type", "N/A"),
            f"[{priority_style}]{req.get('priority', 'N/A')}[/{priority_style}]",
            f"[{status_style}]{req.get('status', 'N/A')}[/{status_style}]",
            req.get("created_at", "")[:10],
        )

    console.print(table)


@requests.command("pending")
def requests_pending():
    """List pending feature requests."""
    store = get_agent_requests_store()
    pending = store.get_pending()

    if not pending:
        console.print("[green]No pending requests - all caught up![/green]")
        return

    console.print(f"[bold]{len(pending)} pending request(s):[/bold]")
    console.print()

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    pending = sorted(pending, key=lambda x: priority_order.get(x.get("priority", "medium"), 2))

    for req in pending:
        priority_style = {
            "critical": "red bold",
            "high": "yellow",
            "medium": "blue",
            "low": "dim",
        }.get(req.get("priority", "medium"), "")

        console.print(Panel(
            f"[bold]{req.get('title', 'Untitled')}[/bold]\n"
            f"Agent: {AGENT_NAMES.get(req.get('agent_id', ''), req.get('agent_id', 'N/A'))}\n"
            f"Priority: [{priority_style}]{req.get('priority', 'N/A')}[/{priority_style}]\n"
            f"Type: {req.get('request_type', 'N/A')}\n\n"
            f"{req.get('description', 'No description')[:200]}",
            title=f"ID: {req['id'][:8]}",
            border_style="yellow"
        ))
        console.print()


@requests.command("show")
@click.argument("request_id")
def requests_show(request_id: str):
    """Show details for a specific request."""
    store = get_agent_requests_store()
    req = store.get_by_id(request_id)

    if not req:
        # Try partial match
        all_requests = store.get_all()
        matches = [r for r in all_requests if r["id"].startswith(request_id)]
        if len(matches) == 1:
            req = matches[0]
        elif len(matches) > 1:
            console.print(f"[yellow]Multiple matches found. Please be more specific.[/yellow]")
            return
        else:
            console.print(f"[red]Request not found: {request_id}[/red]")
            return

    console.print()
    console.print(Panel(f"[bold]{req.get('title', 'Untitled')}[/bold]", border_style="cyan"))
    console.print()
    console.print(f"[bold]ID:[/bold] {req['id']}")
    console.print(f"[bold]Agent:[/bold] {AGENT_NAMES.get(req.get('agent_id', ''), req.get('agent_id', 'N/A'))}")
    console.print(f"[bold]Type:[/bold] {req.get('request_type', 'N/A')}")
    console.print(f"[bold]Priority:[/bold] {req.get('priority', 'N/A')}")
    console.print(f"[bold]Status:[/bold] {req.get('status', 'N/A')}")
    console.print(f"[bold]Created:[/bold] {req.get('created_at', 'N/A')}")
    console.print()
    console.print("[bold]Description:[/bold]")
    console.print(req.get("description", "No description"))
    console.print()

    if req.get("justification"):
        console.print("[bold]Justification:[/bold]")
        console.print(req.get("justification"))
        console.print()

    if req.get("affected_area"):
        console.print(f"[bold]Affected Area:[/bold] {req.get('affected_area')}")
        console.print()

    votes = req.get("votes", {})
    if votes.get("support") or votes.get("oppose"):
        console.print("[bold]Votes:[/bold]")
        if votes.get("support"):
            console.print(f"  [green]Support:[/green] {', '.join(votes['support'])}")
        if votes.get("oppose"):
            console.print(f"  [red]Oppose:[/red] {', '.join(votes['oppose'])}")
        console.print()

    if req.get("reviewed_at"):
        console.print(f"[bold]Reviewed:[/bold] {req.get('reviewed_at')} by {req.get('reviewed_by', 'N/A')}")


@requests.command("create")
@click.option("--agent", "-a", required=True, type=click.Choice(list(AGENT_NAMES.keys())), help="Agent making the request")
@click.option("--title", "-t", required=True, help="Request title")
@click.option("--description", "-d", required=True, help="Detailed description")
@click.option("--type", "request_type", type=click.Choice(["feature", "enhancement", "data", "integration", "ui", "automation", "other"]), default="feature")
@click.option("--priority", "-p", type=click.Choice([p.value for p in FeatureRequestPriority]), default="medium")
@click.option("--justification", "-j", default="", help="Business justification")
@click.option("--area", default="", help="Affected area of the portal")
def requests_create(agent, title, description, request_type, priority, justification, area):
    """Create a new feature request for an agent."""
    store = get_agent_requests_store()

    req = store.create_request(
        agent_id=agent,
        title=title,
        description=description,
        request_type=request_type,
        priority=FeatureRequestPriority(priority),
        justification=justification,
        affected_area=area,
    )

    console.print(f"[green]Created request: {req['id'][:8]} - {req['title']}[/green]")
    console.print(f"Agent: {AGENT_NAMES.get(agent, agent)}")
    console.print(f"Status: {req['status']}")


@requests.command("approve")
@click.argument("request_id")
@click.option("--note", "-n", default="", help="Approval note")
@click.option("--reviewer", "-r", default="Architect", help="Reviewer name")
def requests_approve(request_id: str, note: str, reviewer: str):
    """Approve a feature request."""
    store = get_agent_requests_store()

    # Try partial match
    req = store.get_by_id(request_id)
    if not req:
        all_requests = store.get_all()
        matches = [r for r in all_requests if r["id"].startswith(request_id)]
        if len(matches) == 1:
            request_id = matches[0]["id"]
        elif len(matches) > 1:
            console.print(f"[yellow]Multiple matches found. Please be more specific.[/yellow]")
            return
        else:
            console.print(f"[red]Request not found: {request_id}[/red]")
            return

    result = store.approve(request_id, reviewer, note)

    if result:
        console.print(f"[green]Approved request: {request_id[:8]}[/green]")
    else:
        console.print(f"[red]Failed to approve request[/red]")


@requests.command("reject")
@click.argument("request_id")
@click.option("--reason", "-r", required=True, help="Rejection reason")
@click.option("--reviewer", default="Architect", help="Reviewer name")
def requests_reject(request_id: str, reason: str, reviewer: str):
    """Reject a feature request."""
    store = get_agent_requests_store()

    # Try partial match
    req = store.get_by_id(request_id)
    if not req:
        all_requests = store.get_all()
        matches = [r for r in all_requests if r["id"].startswith(request_id)]
        if len(matches) == 1:
            request_id = matches[0]["id"]
        elif len(matches) > 1:
            console.print(f"[yellow]Multiple matches found. Please be more specific.[/yellow]")
            return
        else:
            console.print(f"[red]Request not found: {request_id}[/red]")
            return

    result = store.reject(request_id, reviewer, reason)

    if result:
        console.print(f"[yellow]Rejected request: {request_id[:8]}[/yellow]")
    else:
        console.print(f"[red]Failed to reject request[/red]")


@requests.command("status")
@click.argument("request_id")
@click.argument("new_status", type=click.Choice([s.value for s in FeatureRequestStatus]))
@click.option("--note", "-n", default="", help="Status update note")
@click.option("--reviewer", "-r", default="Architect", help="Reviewer name")
def requests_status(request_id: str, new_status: str, note: str, reviewer: str):
    """Update request status."""
    store = get_agent_requests_store()

    # Try partial match
    req = store.get_by_id(request_id)
    if not req:
        all_requests = store.get_all()
        matches = [r for r in all_requests if r["id"].startswith(request_id)]
        if len(matches) == 1:
            request_id = matches[0]["id"]
        elif len(matches) > 1:
            console.print(f"[yellow]Multiple matches found. Please be more specific.[/yellow]")
            return
        else:
            console.print(f"[red]Request not found: {request_id}[/red]")
            return

    result = store.update_status(request_id, FeatureRequestStatus(new_status), reviewer, note)

    if result:
        console.print(f"[green]Updated request {request_id[:8]} status to: {new_status}[/green]")
    else:
        console.print(f"[red]Failed to update request status[/red]")


@requests.command("vote")
@click.argument("request_id")
@click.argument("voter_agent", type=click.Choice(list(AGENT_NAMES.keys())))
@click.option("--type", "vote_type", type=click.Choice(["support", "oppose"]), default="support", help="Vote type")
def requests_vote(request_id: str, voter_agent: str, vote_type: str):
    """Cast a vote on a request (as another agent)."""
    store = get_agent_requests_store()

    # Try partial match
    req = store.get_by_id(request_id)
    if not req:
        all_requests = store.get_all()
        matches = [r for r in all_requests if r["id"].startswith(request_id)]
        if len(matches) == 1:
            request_id = matches[0]["id"]
        elif len(matches) > 1:
            console.print(f"[yellow]Multiple matches found. Please be more specific.[/yellow]")
            return
        else:
            console.print(f"[red]Request not found: {request_id}[/red]")
            return

    result = store.vote(request_id, voter_agent, vote_type)

    if result:
        console.print(f"[green]Recorded {vote_type} vote from {AGENT_NAMES.get(voter_agent, voter_agent)} on request {request_id[:8]}[/green]")
    else:
        console.print(f"[red]Failed to record vote[/red]")
