"""
Data Store Module for Rinse Repeat Labs

Manages structured data for:
- Ideas (app submissions)
- Testers (beta tester program)
- Clients (company/individual relationships)
- Projects (active development work)
- Finances (invoices, payments, revenue shares)
- Communications (email/message history)
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict
from enum import Enum

import config


# =============================================================================
# DATA DIRECTORY
# =============================================================================

DATA_DIR = config.BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# =============================================================================
# ENUMS
# =============================================================================

class IdeaStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_DEVELOPMENT = "in_development"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class TesterStatus(str, Enum):
    APPLIED = "applied"
    APPROVED = "approved"
    ACTIVE = "active"
    INACTIVE = "inactive"
    REJECTED = "rejected"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    DESIGN = "design"
    DEVELOPMENT = "development"
    QA = "qa"
    LAUNCH = "launch"
    MAINTENANCE = "maintenance"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentType(str, Enum):
    CLIENT_PAYMENT = "client_payment"
    TESTER_PAYMENT = "tester_payment"
    CONTRACTOR_PAYMENT = "contractor_payment"
    REVENUE_SHARE = "revenue_share"
    EXPENSE = "expense"


class FeatureRequestStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    DEFERRED = "deferred"


class FeatureRequestPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# BASE DATA STORE
# =============================================================================

class DataStore:
    """Generic JSON-based data store."""

    def __init__(self, name: str):
        self.name = name
        self.file_path = DATA_DIR / f"{name}.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure the data file exists."""
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict[str, Any]]:
        """Load all records."""
        content = self.file_path.read_text(encoding="utf-8")
        return json.loads(content) if content.strip() else []

    def _save(self, records: list[dict[str, Any]]) -> None:
        """Save all records."""
        self.file_path.write_text(
            json.dumps(records, indent=2, default=str),
            encoding="utf-8"
        )

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())[:8]

    def get_all(self) -> list[dict[str, Any]]:
        """Get all records."""
        return self._load()

    def get_by_id(self, record_id: str) -> dict[str, Any] | None:
        """Get a record by ID."""
        records = self._load()
        for record in records:
            if record.get("id") == record_id:
                return record
        return None

    def query(self, **filters) -> list[dict[str, Any]]:
        """Query records by field values."""
        records = self._load()
        results = []
        for record in records:
            match = True
            for key, value in filters.items():
                if key not in record:
                    match = False
                    break
                if isinstance(value, str) and isinstance(record[key], str):
                    if value.lower() not in record[key].lower():
                        match = False
                        break
                elif record[key] != value:
                    match = False
                    break
            if match:
                results.append(record)
        return results

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new record."""
        records = self._load()
        record = {
            "id": self._generate_id(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **data
        }
        records.append(record)
        self._save(records)
        return record

    def update(self, record_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update a record by ID."""
        records = self._load()
        for i, record in enumerate(records):
            if record.get("id") == record_id:
                records[i] = {
                    **record,
                    **data,
                    "id": record_id,
                    "created_at": record.get("created_at"),
                    "updated_at": datetime.now().isoformat(),
                }
                self._save(records)
                return records[i]
        return None

    def delete(self, record_id: str) -> bool:
        """Delete a record by ID."""
        records = self._load()
        for i, record in enumerate(records):
            if record.get("id") == record_id:
                records.pop(i)
                self._save(records)
                return True
        return False

    def add_note(self, record_id: str, note: str, author: str = "system") -> dict[str, Any] | None:
        """Add a note to a record's history."""
        record = self.get_by_id(record_id)
        if not record:
            return None

        notes = record.get("notes", [])
        notes.append({
            "timestamp": datetime.now().isoformat(),
            "author": author,
            "content": note
        })

        return self.update(record_id, {"notes": notes})


# =============================================================================
# IDEAS STORE
# =============================================================================

class IdeasStore(DataStore):
    """Store for app idea submissions."""

    def __init__(self):
        super().__init__("ideas")

    def create_idea(
        self,
        name: str,
        description: str,
        submitter_name: str,
        submitter_email: str,
        submitter_company: str = "",
        platforms: list[str] | None = None,
        revenue_model: str = "",
        timeline: str = "",
        budget_range: str = "",
        features: list[str] | None = None,
        competitors: str = "",
        differentiation: str = "",
    ) -> dict[str, Any]:
        """Create a new idea submission."""
        return self.create({
            "name": name,
            "description": description,
            "submitter": {
                "name": submitter_name,
                "email": submitter_email,
                "company": submitter_company,
            },
            "platforms": platforms or [],
            "revenue_model": revenue_model,
            "timeline": timeline,
            "budget_range": budget_range,
            "features": features or [],
            "competitors": competitors,
            "differentiation": differentiation,
            "status": IdeaStatus.SUBMITTED.value,
            "review": None,  # Populated after idea review meeting
            "communications": [],
            "notes": [],
        })

    def update_status(self, idea_id: str, status: IdeaStatus, note: str = "") -> dict[str, Any] | None:
        """Update idea status with optional note."""
        result = self.update(idea_id, {"status": status.value})
        if result and note:
            self.add_note(idea_id, f"Status changed to {status.value}: {note}")
        return result

    def add_review(
        self,
        idea_id: str,
        recommendation: str,
        confidence: str,
        tech_assessment: dict,
        financial_assessment: dict,
        timeline_estimate: str,
        concerns: list[str],
        next_steps: list[str],
    ) -> dict[str, Any] | None:
        """Add review results from idea review meeting."""
        return self.update(idea_id, {
            "review": {
                "date": datetime.now().isoformat(),
                "recommendation": recommendation,  # GO, GO_WITH_MODIFICATIONS, NO_GO
                "confidence": confidence,  # High, Medium, Low
                "tech_assessment": tech_assessment,
                "financial_assessment": financial_assessment,
                "timeline_estimate": timeline_estimate,
                "concerns": concerns,
                "next_steps": next_steps,
            }
        })

    def add_communication(
        self,
        idea_id: str,
        direction: str,  # "inbound" or "outbound"
        channel: str,  # "email", "phone", "meeting"
        subject: str,
        content: str,
        sender: str,
    ) -> dict[str, Any] | None:
        """Log a communication with the submitter."""
        record = self.get_by_id(idea_id)
        if not record:
            return None

        comms = record.get("communications", [])
        comms.append({
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "channel": channel,
            "subject": subject,
            "content": content,
            "sender": sender,
        })

        return self.update(idea_id, {"communications": comms})

    def get_pending(self) -> list[dict[str, Any]]:
        """Get ideas pending review."""
        return self.query(status=IdeaStatus.SUBMITTED.value)

    def get_under_review(self) -> list[dict[str, Any]]:
        """Get ideas currently under review."""
        return self.query(status=IdeaStatus.UNDER_REVIEW.value)

    def get_approved(self) -> list[dict[str, Any]]:
        """Get approved ideas."""
        return self.query(status=IdeaStatus.APPROVED.value)


# =============================================================================
# TESTERS STORE
# =============================================================================

class TestersStore(DataStore):
    """Store for beta tester program."""

    def __init__(self):
        super().__init__("testers")

    def create_tester(
        self,
        name: str,
        email: str,
        devices: list[dict[str, str]],  # [{"type": "iPhone", "model": "14 Pro", "os": "iOS 17"}]
        experience_level: str,  # "new", "some", "experienced", "professional"
        hours_per_week: int,
        payment_method: str,  # "paypal", "venmo", "crypto"
        payment_details: str,  # email or wallet address
        location: str = "",
        languages: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register a new beta tester."""
        return self.create({
            "name": name,
            "email": email,
            "devices": devices,
            "experience_level": experience_level,
            "hours_per_week": hours_per_week,
            "payment": {
                "method": payment_method,
                "details": payment_details,
            },
            "location": location,
            "languages": languages or ["English"],
            "status": TesterStatus.APPLIED.value,
            "projects": [],  # List of project IDs they've tested
            "feedback_count": 0,
            "total_earned": 0.0,
            "rating": None,  # 1-5 rating based on feedback quality
            "communications": [],
            "notes": [],
        })

    def approve(self, tester_id: str, note: str = "") -> dict[str, Any] | None:
        """Approve a tester application."""
        result = self.update(tester_id, {"status": TesterStatus.APPROVED.value})
        if result and note:
            self.add_note(tester_id, f"Application approved: {note}", author="QALead")
        return result

    def reject(self, tester_id: str, reason: str) -> dict[str, Any] | None:
        """Reject a tester application."""
        result = self.update(tester_id, {"status": TesterStatus.REJECTED.value})
        if result:
            self.add_note(tester_id, f"Application rejected: {reason}", author="QALead")
        return result

    def assign_to_project(self, tester_id: str, project_id: str) -> dict[str, Any] | None:
        """Assign a tester to a project."""
        record = self.get_by_id(tester_id)
        if not record:
            return None

        projects = record.get("projects", [])
        if project_id not in projects:
            projects.append(project_id)

        return self.update(tester_id, {
            "projects": projects,
            "status": TesterStatus.ACTIVE.value,
        })

    def record_payment(self, tester_id: str, amount: float, project_id: str) -> dict[str, Any] | None:
        """Record a payment to a tester."""
        record = self.get_by_id(tester_id)
        if not record:
            return None

        total = record.get("total_earned", 0.0) + amount
        self.add_note(tester_id, f"Payment of ${amount:.2f} for project {project_id}", author="CFO")
        return self.update(tester_id, {"total_earned": total})

    def update_rating(self, tester_id: str, rating: float) -> dict[str, Any] | None:
        """Update tester quality rating (1-5)."""
        return self.update(tester_id, {"rating": min(5.0, max(1.0, rating))})

    def get_by_device_type(self, device_type: str) -> list[dict[str, Any]]:
        """Get testers who have a specific device type."""
        all_testers = self.get_all()
        results = []
        for tester in all_testers:
            for device in tester.get("devices", []):
                if device_type.lower() in device.get("type", "").lower():
                    results.append(tester)
                    break
        return results

    def get_available(self) -> list[dict[str, Any]]:
        """Get testers who are approved and available."""
        return [t for t in self.get_all()
                if t.get("status") in [TesterStatus.APPROVED.value, TesterStatus.ACTIVE.value]]


# =============================================================================
# CLIENTS STORE
# =============================================================================

class ClientsStore(DataStore):
    """Store for client relationships."""

    def __init__(self):
        super().__init__("clients")

    def create_client(
        self,
        name: str,
        company: str,
        email: str,
        phone: str = "",
        address: str = "",
        billing_email: str = "",
        primary_contact: str = "",
        source: str = "",  # How they found us
    ) -> dict[str, Any]:
        """Create a new client record."""
        return self.create({
            "name": name,
            "company": company,
            "email": email,
            "phone": phone,
            "address": address,
            "billing_email": billing_email or email,
            "primary_contact": primary_contact or name,
            "source": source,
            "projects": [],  # List of project IDs
            "ideas": [],  # List of idea IDs
            "total_revenue": 0.0,
            "total_invoiced": 0.0,
            "total_paid": 0.0,
            "status": "active",
            "communications": [],
            "notes": [],
        })

    def link_idea(self, client_id: str, idea_id: str) -> dict[str, Any] | None:
        """Link an idea to a client."""
        record = self.get_by_id(client_id)
        if not record:
            return None

        ideas = record.get("ideas", [])
        if idea_id not in ideas:
            ideas.append(idea_id)

        return self.update(client_id, {"ideas": ideas})

    def link_project(self, client_id: str, project_id: str) -> dict[str, Any] | None:
        """Link a project to a client."""
        record = self.get_by_id(client_id)
        if not record:
            return None

        projects = record.get("projects", [])
        if project_id not in projects:
            projects.append(project_id)

        return self.update(client_id, {"projects": projects})

    def update_financials(
        self,
        client_id: str,
        invoiced: float = 0,
        paid: float = 0,
        revenue: float = 0,
    ) -> dict[str, Any] | None:
        """Update client financial totals."""
        record = self.get_by_id(client_id)
        if not record:
            return None

        return self.update(client_id, {
            "total_invoiced": record.get("total_invoiced", 0) + invoiced,
            "total_paid": record.get("total_paid", 0) + paid,
            "total_revenue": record.get("total_revenue", 0) + revenue,
        })


# =============================================================================
# PROJECTS STORE
# =============================================================================

class ProjectsStore(DataStore):
    """Store for development projects."""

    def __init__(self):
        super().__init__("projects")

    def create_project(
        self,
        name: str,
        client_id: str,
        idea_id: str = "",
        description: str = "",
        platforms: list[str] | None = None,
        tech_stack: list[str] | None = None,
        revenue_model: str = "",  # "full_payment", "70_30", "50_50"
        contract_value: float = 0,
        start_date: str = "",
        target_launch: str = "",
        team: list[str] | None = None,  # List of agent IDs assigned
    ) -> dict[str, Any]:
        """Create a new project."""
        return self.create({
            "name": name,
            "client_id": client_id,
            "idea_id": idea_id,
            "description": description,
            "platforms": platforms or [],
            "tech_stack": tech_stack or [],
            "revenue_model": revenue_model,
            "contract_value": contract_value,
            "start_date": start_date or datetime.now().strftime("%Y-%m-%d"),
            "target_launch": target_launch,
            "actual_launch": "",
            "team": team or ["pm", "dev_lead", "design_lead", "qa_lead"],
            "status": ProjectStatus.PLANNING.value,
            "testers": [],  # List of tester IDs
            "milestones": [],
            "sprints": [],
            "financials": {
                "invoiced": 0,
                "paid": 0,
                "revenue_share_earned": 0,
                "expenses": 0,
            },
            "notes": [],
        })

    def update_status(self, project_id: str, status: ProjectStatus, note: str = "") -> dict[str, Any] | None:
        """Update project status."""
        result = self.update(project_id, {"status": status.value})
        if result and note:
            self.add_note(project_id, f"Status changed to {status.value}: {note}", author="PM")
        return result

    def add_milestone(
        self,
        project_id: str,
        name: str,
        due_date: str,
        deliverables: list[str],
    ) -> dict[str, Any] | None:
        """Add a milestone to the project."""
        record = self.get_by_id(project_id)
        if not record:
            return None

        milestones = record.get("milestones", [])
        milestones.append({
            "id": self._generate_id(),
            "name": name,
            "due_date": due_date,
            "deliverables": deliverables,
            "completed": False,
            "completed_date": None,
        })

        return self.update(project_id, {"milestones": milestones})

    def complete_milestone(self, project_id: str, milestone_id: str) -> dict[str, Any] | None:
        """Mark a milestone as completed."""
        record = self.get_by_id(project_id)
        if not record:
            return None

        milestones = record.get("milestones", [])
        for m in milestones:
            if m.get("id") == milestone_id:
                m["completed"] = True
                m["completed_date"] = datetime.now().isoformat()
                break

        return self.update(project_id, {"milestones": milestones})

    def assign_tester(self, project_id: str, tester_id: str) -> dict[str, Any] | None:
        """Assign a tester to the project."""
        record = self.get_by_id(project_id)
        if not record:
            return None

        testers = record.get("testers", [])
        if tester_id not in testers:
            testers.append(tester_id)

        return self.update(project_id, {"testers": testers})

    def get_active(self) -> list[dict[str, Any]]:
        """Get active projects."""
        all_projects = self.get_all()
        active_statuses = [
            ProjectStatus.PLANNING.value,
            ProjectStatus.DESIGN.value,
            ProjectStatus.DEVELOPMENT.value,
            ProjectStatus.QA.value,
            ProjectStatus.LAUNCH.value,
        ]
        return [p for p in all_projects if p.get("status") in active_statuses]


# =============================================================================
# FINANCES STORE
# =============================================================================

class FinancesStore(DataStore):
    """Store for financial transactions."""

    def __init__(self):
        super().__init__("finances")

    def create_invoice(
        self,
        client_id: str,
        project_id: str,
        amount: float,
        description: str,
        due_date: str,
        line_items: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Create a new invoice."""
        invoice_num = f"INV-{datetime.now().strftime('%Y%m%d')}-{self._generate_id()[:4].upper()}"
        return self.create({
            "type": "invoice",
            "invoice_number": invoice_num,
            "client_id": client_id,
            "project_id": project_id,
            "amount": amount,
            "description": description,
            "due_date": due_date,
            "line_items": line_items or [{"description": description, "amount": amount}],
            "status": InvoiceStatus.DRAFT.value,
            "sent_date": None,
            "paid_date": None,
            "notes": [],
        })

    def record_payment(
        self,
        payment_type: PaymentType,
        amount: float,
        description: str,
        reference_id: str = "",  # client_id, tester_id, etc.
        project_id: str = "",
        invoice_id: str = "",
    ) -> dict[str, Any]:
        """Record a payment (incoming or outgoing)."""
        return self.create({
            "type": "payment",
            "payment_type": payment_type.value,
            "amount": amount,
            "description": description,
            "reference_id": reference_id,
            "project_id": project_id,
            "invoice_id": invoice_id,
            "notes": [],
        })

    def record_expense(
        self,
        amount: float,
        category: str,
        description: str,
        vendor: str = "",
        project_id: str = "",
    ) -> dict[str, Any]:
        """Record an expense."""
        return self.create({
            "type": "expense",
            "amount": amount,
            "category": category,
            "description": description,
            "vendor": vendor,
            "project_id": project_id,
            "notes": [],
        })

    def record_revenue_share(
        self,
        client_id: str,
        project_id: str,
        gross_revenue: float,
        our_share_percent: float,
        our_share_amount: float,
        period: str,  # e.g., "2026-01"
    ) -> dict[str, Any]:
        """Record revenue share earnings."""
        return self.create({
            "type": "revenue_share",
            "client_id": client_id,
            "project_id": project_id,
            "gross_revenue": gross_revenue,
            "our_share_percent": our_share_percent,
            "our_share_amount": our_share_amount,
            "period": period,
            "notes": [],
        })

    def mark_invoice_sent(self, invoice_id: str) -> dict[str, Any] | None:
        """Mark an invoice as sent."""
        return self.update(invoice_id, {
            "status": InvoiceStatus.SENT.value,
            "sent_date": datetime.now().isoformat(),
        })

    def mark_invoice_paid(self, invoice_id: str) -> dict[str, Any] | None:
        """Mark an invoice as paid."""
        return self.update(invoice_id, {
            "status": InvoiceStatus.PAID.value,
            "paid_date": datetime.now().isoformat(),
        })

    def get_invoices(self, status: InvoiceStatus | None = None) -> list[dict[str, Any]]:
        """Get invoices, optionally filtered by status."""
        invoices = self.query(type="invoice")
        if status:
            invoices = [i for i in invoices if i.get("status") == status.value]
        return invoices

    def get_outstanding_balance(self, client_id: str) -> float:
        """Get total outstanding balance for a client."""
        invoices = self.query(type="invoice", client_id=client_id)
        outstanding = sum(
            i.get("amount", 0)
            for i in invoices
            if i.get("status") in [InvoiceStatus.SENT.value, InvoiceStatus.OVERDUE.value]
        )
        return outstanding

    def get_revenue_by_period(self, period: str) -> dict[str, float]:
        """Get revenue breakdown for a period."""
        all_records = self.get_all()
        payments = [r for r in all_records
                   if r.get("type") == "payment"
                   and r.get("payment_type") == PaymentType.CLIENT_PAYMENT.value
                   and r.get("created_at", "").startswith(period)]
        revenue_shares = [r for r in all_records
                        if r.get("type") == "revenue_share"
                        and r.get("period") == period]
        expenses = [r for r in all_records
                   if r.get("type") == "expense"
                   and r.get("created_at", "").startswith(period)]

        return {
            "client_payments": sum(p.get("amount", 0) for p in payments),
            "revenue_share": sum(r.get("our_share_amount", 0) for r in revenue_shares),
            "expenses": sum(e.get("amount", 0) for e in expenses),
            "net": (
                sum(p.get("amount", 0) for p in payments) +
                sum(r.get("our_share_amount", 0) for r in revenue_shares) -
                sum(e.get("amount", 0) for e in expenses)
            ),
        }


# =============================================================================
# AGENT REQUESTS STORE
# =============================================================================

class AgentRequestsStore(DataStore):
    """Store for agent feature requests and portal customizations."""

    def __init__(self):
        super().__init__("agent_requests")

    def create_request(
        self,
        agent_id: str,
        title: str,
        description: str,
        request_type: str = "feature",  # feature, bug, enhancement, content
        priority: FeatureRequestPriority = FeatureRequestPriority.MEDIUM,
        justification: str = "",
        affected_area: str = "",  # portal section affected
    ) -> dict[str, Any]:
        """Create a new feature request from an agent."""
        return self.create({
            "agent_id": agent_id,
            "title": title,
            "description": description,
            "request_type": request_type,
            "priority": priority.value if isinstance(priority, FeatureRequestPriority) else priority,
            "justification": justification,
            "affected_area": affected_area,
            "status": FeatureRequestStatus.SUBMITTED.value,
            "submitted_at": datetime.now().isoformat(),
            "reviewed_at": None,
            "reviewed_by": None,
            "review_notes": "",
            "implemented_at": None,
            "notes": [],
            "votes": [],  # Other agents can vote on requests
        })

    def update_status(
        self,
        request_id: str,
        new_status: FeatureRequestStatus,
        reviewer: str = "Architect",
        notes: str = "",
    ) -> dict[str, Any] | None:
        """Update the status of a feature request."""
        update_data = {
            "status": new_status.value if isinstance(new_status, FeatureRequestStatus) else new_status,
            "reviewed_at": datetime.now().isoformat(),
            "reviewed_by": reviewer,
        }
        if notes:
            update_data["review_notes"] = notes

        if new_status == FeatureRequestStatus.IMPLEMENTED:
            update_data["implemented_at"] = datetime.now().isoformat()

        result = self.update(request_id, update_data)
        if result and notes:
            self.add_note(request_id, f"Status changed to {new_status.value}: {notes}", reviewer)
        return result

    def approve(self, request_id: str, reviewer: str = "Architect", notes: str = "") -> dict[str, Any] | None:
        """Approve a feature request."""
        return self.update_status(request_id, FeatureRequestStatus.APPROVED, reviewer, notes)

    def reject(self, request_id: str, reviewer: str = "Architect", reason: str = "") -> dict[str, Any] | None:
        """Reject a feature request."""
        return self.update_status(request_id, FeatureRequestStatus.REJECTED, reviewer, reason)

    def vote(self, request_id: str, agent_id: str, vote_type: str = "support") -> dict[str, Any] | None:
        """Allow an agent to vote on a request."""
        record = self.get_by_id(request_id)
        if not record:
            return None

        votes = record.get("votes", [])
        # Remove existing vote from this agent
        votes = [v for v in votes if v.get("agent_id") != agent_id]
        # Add new vote
        votes.append({
            "agent_id": agent_id,
            "vote_type": vote_type,  # support, oppose, neutral
            "timestamp": datetime.now().isoformat(),
        })

        return self.update(request_id, {"votes": votes})

    def get_by_agent(self, agent_id: str) -> list[dict[str, Any]]:
        """Get all requests from a specific agent."""
        return self.query(agent_id=agent_id)

    def get_pending(self) -> list[dict[str, Any]]:
        """Get all pending requests awaiting review."""
        all_requests = self.get_all()
        return [r for r in all_requests if r.get("status") in [
            FeatureRequestStatus.SUBMITTED.value,
            FeatureRequestStatus.UNDER_REVIEW.value,
        ]]

    def get_approved(self) -> list[dict[str, Any]]:
        """Get all approved requests not yet implemented."""
        return self.query(status=FeatureRequestStatus.APPROVED.value)

    def get_by_status(self, status: FeatureRequestStatus) -> list[dict[str, Any]]:
        """Get requests by status."""
        return self.query(status=status.value if isinstance(status, FeatureRequestStatus) else status)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Singleton instances
_ideas_store: IdeasStore | None = None
_testers_store: TestersStore | None = None
_clients_store: ClientsStore | None = None
_projects_store: ProjectsStore | None = None
_finances_store: FinancesStore | None = None
_agent_requests_store: AgentRequestsStore | None = None


def get_ideas_store() -> IdeasStore:
    """Get the ideas store singleton."""
    global _ideas_store
    if _ideas_store is None:
        _ideas_store = IdeasStore()
    return _ideas_store


def get_testers_store() -> TestersStore:
    """Get the testers store singleton."""
    global _testers_store
    if _testers_store is None:
        _testers_store = TestersStore()
    return _testers_store


def get_clients_store() -> ClientsStore:
    """Get the clients store singleton."""
    global _clients_store
    if _clients_store is None:
        _clients_store = ClientsStore()
    return _clients_store


def get_projects_store() -> ProjectsStore:
    """Get the projects store singleton."""
    global _projects_store
    if _projects_store is None:
        _projects_store = ProjectsStore()
    return _projects_store


def get_finances_store() -> FinancesStore:
    """Get the finances store singleton."""
    global _finances_store
    if _finances_store is None:
        _finances_store = FinancesStore()
    return _finances_store


def get_agent_requests_store() -> AgentRequestsStore:
    """Get the agent requests store singleton."""
    global _agent_requests_store
    if _agent_requests_store is None:
        _agent_requests_store = AgentRequestsStore()
    return _agent_requests_store
