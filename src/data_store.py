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

    def get_payments(self, payment_type: PaymentType | None = None) -> list[dict[str, Any]]:
        """Get payments, optionally filtered by type."""
        payments = self.query(type="payment")
        if payment_type:
            payments = [p for p in payments if p.get("payment_type") == payment_type.value]
        return sorted(payments, key=lambda x: x.get("created_at", ""), reverse=True)

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
# SETTINGS STORE
# =============================================================================

# Industry presets with agent role descriptions
INDUSTRY_PRESETS = {
    "software_development": {
        "name": "Software Development",
        "description": "App development studio building mobile and web applications",
        "default_company_name": "Rinse Repeat Labs",
        "default_tagline": "App Development Studio",
        "agent_roles": {
            "ceo": "Strategic leadership and company direction for the development studio",
            "cfo": "Financial planning, pricing strategies, and project budgeting",
            "cito": "Technical strategy, architecture decisions, and technology evaluation",
            "sales": "Client acquisition, project scoping, and partnership development",
            "legal": "Contracts, IP protection, and software licensing compliance",
            "dev_lead": "Engineering leadership, code quality, and technical implementation",
            "design_lead": "UI/UX design, design systems, and user experience",
            "qa_lead": "Quality assurance, testing strategy, and beta tester program",
            "pm": "Project coordination, sprint planning, and delivery management",
            "customer_success": "Client relationships, onboarding, and satisfaction",
            "marketing": "App store optimization, growth marketing, and brand awareness",
            "support": "Customer support, documentation, and issue resolution",
        }
    },
    "marketing_agency": {
        "name": "Marketing Agency",
        "description": "Full-service marketing agency handling campaigns and brand strategy",
        "default_company_name": "Your Agency Name",
        "default_tagline": "Marketing Agency",
        "agent_roles": {
            "ceo": "Agency leadership, vision, and key client relationships",
            "cfo": "Agency finances, retainer management, and profitability",
            "cito": "Marketing technology stack, automation, and analytics platforms",
            "sales": "New business development, pitches, and proposal creation",
            "legal": "Client contracts, media rights, and compliance",
            "dev_lead": "Website development, landing pages, and technical marketing",
            "design_lead": "Creative direction, brand identity, and visual campaigns",
            "qa_lead": "Campaign quality checks, A/B testing, and performance review",
            "pm": "Campaign management, timelines, and resource allocation",
            "customer_success": "Account management and client retention",
            "marketing": "Strategy development, media planning, and execution",
            "support": "Client communications and deliverable management",
        }
    },
    "consulting_firm": {
        "name": "Consulting Firm",
        "description": "Professional services firm providing business consulting",
        "default_company_name": "Your Firm Name",
        "default_tagline": "Business Consulting",
        "agent_roles": {
            "ceo": "Firm leadership, thought leadership, and strategic partnerships",
            "cfo": "Engagement pricing, utilization tracking, and firm finances",
            "cito": "Knowledge management, research tools, and data analytics",
            "sales": "Business development, proposal writing, and client acquisition",
            "legal": "Engagement letters, liability, and regulatory compliance",
            "dev_lead": "Internal tools, automation, and technical solutions",
            "design_lead": "Presentation design, report formatting, and brand materials",
            "qa_lead": "Deliverable quality, methodology adherence, and peer review",
            "pm": "Engagement management, resource planning, and timelines",
            "customer_success": "Client relationship management and renewals",
            "marketing": "Thought leadership, events, and firm positioning",
            "support": "Research support, scheduling, and administrative coordination",
        }
    },
    "ecommerce_business": {
        "name": "E-Commerce Business",
        "description": "Online retail business selling products directly to consumers",
        "default_company_name": "Your Store Name",
        "default_tagline": "E-Commerce",
        "agent_roles": {
            "ceo": "Business strategy, supplier relationships, and growth direction",
            "cfo": "Inventory costs, margins, cash flow, and financial planning",
            "cito": "E-commerce platform, integrations, and technology infrastructure",
            "sales": "B2B wholesale, partnerships, and marketplace expansion",
            "legal": "Consumer protection, returns policy, and supplier contracts",
            "dev_lead": "Website development, checkout optimization, and integrations",
            "design_lead": "Product photography, branding, and user experience",
            "qa_lead": "Product quality control, order accuracy, and testing",
            "pm": "Product launches, seasonal planning, and inventory coordination",
            "customer_success": "VIP customers, loyalty programs, and retention",
            "marketing": "Digital advertising, SEO, email marketing, and promotions",
            "support": "Customer service, returns, and order inquiries",
        }
    },
    "creative_agency": {
        "name": "Creative Agency",
        "description": "Design and creative services agency for branding and content",
        "default_company_name": "Your Studio Name",
        "default_tagline": "Creative Agency",
        "agent_roles": {
            "ceo": "Creative vision, agency culture, and key client relationships",
            "cfo": "Project pricing, freelancer payments, and agency finances",
            "cito": "Creative tools, asset management, and production technology",
            "sales": "New business pitches, RFP responses, and client acquisition",
            "legal": "Usage rights, licensing, and creative contracts",
            "dev_lead": "Digital production, motion graphics, and interactive work",
            "design_lead": "Art direction, brand development, and visual design",
            "qa_lead": "Creative review, brand consistency, and quality standards",
            "pm": "Project timelines, resource scheduling, and delivery",
            "customer_success": "Account management and creative partnerships",
            "marketing": "Agency promotion, awards, and industry presence",
            "support": "Asset delivery, revisions, and client communications",
        }
    },
    "professional_services": {
        "name": "Professional Services",
        "description": "Service-based business providing specialized expertise",
        "default_company_name": "Your Business Name",
        "default_tagline": "Professional Services",
        "agent_roles": {
            "ceo": "Business leadership, expertise positioning, and strategic growth",
            "cfo": "Service pricing, billing, and financial management",
            "cito": "Service delivery tools, scheduling, and technology systems",
            "sales": "Lead generation, consultations, and service sales",
            "legal": "Service agreements, liability, and compliance",
            "dev_lead": "Internal systems, automation, and digital tools",
            "design_lead": "Brand materials, proposals, and presentation design",
            "qa_lead": "Service quality, client satisfaction, and standards",
            "pm": "Engagement scheduling, resource planning, and delivery",
            "customer_success": "Client relationships, renewals, and referrals",
            "marketing": "Reputation building, content marketing, and lead generation",
            "support": "Client inquiries, scheduling, and service coordination",
        }
    },
    "custom": {
        "name": "Custom",
        "description": "Define your own company type and agent roles",
        "default_company_name": "Your Company Name",
        "default_tagline": "Your Tagline",
        "agent_roles": {
            "ceo": "Chief Executive - overall leadership and strategy",
            "cfo": "Chief Financial Officer - finances and budgeting",
            "cito": "Chief Information/Technology Officer - technology strategy",
            "sales": "Sales Director - business development and revenue",
            "legal": "Legal Counsel - contracts and compliance",
            "dev_lead": "Development/Operations Lead - implementation and delivery",
            "design_lead": "Design/Creative Lead - design and user experience",
            "qa_lead": "Quality Assurance Lead - quality and standards",
            "pm": "Project Manager - coordination and delivery",
            "customer_success": "Customer Success - client relationships",
            "marketing": "Marketing Director - promotion and growth",
            "support": "Support Lead - customer service and help",
        }
    }
}


class SettingsStore:
    """Store for company settings and configuration."""

    def __init__(self):
        self.file_path = DATA_DIR / "settings.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure the settings file exists with defaults."""
        if not self.file_path.exists():
            self._save(self._get_defaults())

    def _get_defaults(self) -> dict[str, Any]:
        """Get default settings."""
        return {
            "company_name": "Rinse Repeat Labs",
            "company_tagline": "App Development Studio",
            "industry": "software_development",
            "custom_agent_roles": {},  # Override specific agent roles
            "theme": "light",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def _load(self) -> dict[str, Any]:
        """Load settings."""
        content = self.file_path.read_text(encoding="utf-8")
        if not content.strip():
            return self._get_defaults()
        settings = json.loads(content)
        # Merge with defaults to ensure all keys exist
        defaults = self._get_defaults()
        for key, value in defaults.items():
            if key not in settings:
                settings[key] = value
        return settings

    def _save(self, settings: dict[str, Any]) -> None:
        """Save settings."""
        settings["updated_at"] = datetime.now().isoformat()
        self.file_path.write_text(
            json.dumps(settings, indent=2, default=str),
            encoding="utf-8"
        )

    def get(self) -> dict[str, Any]:
        """Get all settings."""
        settings = self._load()
        # Add computed fields
        industry = settings.get("industry", "software_development")
        preset = INDUSTRY_PRESETS.get(industry, INDUSTRY_PRESETS["software_development"])
        settings["industry_name"] = preset["name"]
        settings["industry_description"] = preset["description"]
        return settings

    def update(self, updates: dict[str, Any]) -> dict[str, Any]:
        """Update settings."""
        settings = self._load()
        settings.update(updates)
        self._save(settings)
        return self.get()

    def get_company_name(self) -> str:
        """Get the company name."""
        return self._load().get("company_name", "Rinse Repeat Labs")

    def get_company_tagline(self) -> str:
        """Get the company tagline."""
        return self._load().get("company_tagline", "App Development Studio")

    def get_industry(self) -> str:
        """Get the current industry setting."""
        return self._load().get("industry", "software_development")

    def get_industry_preset(self) -> dict[str, Any]:
        """Get the current industry preset."""
        industry = self.get_industry()
        return INDUSTRY_PRESETS.get(industry, INDUSTRY_PRESETS["software_development"])

    def get_agent_role(self, agent_id: str) -> str:
        """Get the role description for an agent."""
        settings = self._load()
        # Check for custom override first
        custom_roles = settings.get("custom_agent_roles", {})
        if agent_id in custom_roles:
            return custom_roles[agent_id]
        # Fall back to industry preset
        preset = self.get_industry_preset()
        return preset["agent_roles"].get(agent_id, "Team member")

    def set_industry(self, industry: str) -> dict[str, Any]:
        """Set the industry and optionally update company name/tagline to defaults."""
        if industry not in INDUSTRY_PRESETS:
            industry = "custom"
        preset = INDUSTRY_PRESETS[industry]
        updates = {"industry": industry}
        # Only update name/tagline if they match the old preset defaults
        current = self._load()
        old_preset = INDUSTRY_PRESETS.get(current.get("industry", "software_development"), {})
        if current.get("company_name") == old_preset.get("default_company_name"):
            updates["company_name"] = preset["default_company_name"]
        if current.get("company_tagline") == old_preset.get("default_tagline"):
            updates["company_tagline"] = preset["default_tagline"]
        return self.update(updates)

    def reset_to_defaults(self) -> dict[str, Any]:
        """Reset all settings to defaults."""
        self._save(self._get_defaults())
        return self.get()

    @staticmethod
    def get_available_industries() -> dict[str, dict[str, str]]:
        """Get list of available industry presets."""
        return {
            key: {"name": value["name"], "description": value["description"]}
            for key, value in INDUSTRY_PRESETS.items()
        }


# =============================================================================
# AGENT DOCUMENTATION - Under the Hood
# =============================================================================

AGENT_DOCUMENTATION = {
    "ceo": {
        "how_it_works": """The CEO agent serves as the strategic leader of your AI team. When you engage in meetings, the CEO:

1. **Processes Context** - Reviews company.md, active projects, and recent decisions before responding
2. **Maintains Vision** - Keeps responses aligned with company goals and values
3. **Delegates Appropriately** - Knows when to involve other agents or defer to specialists
4. **Tracks Decisions** - All major decisions are logged to decisions/decisions.json""",
        "collaboration": {
            "reports_to": "Architect (You)",
            "direct_reports": ["CFO", "CITO", "Sales", "Legal", "PM", "Marketing"],
            "collaborates_with": ["All agents for strategic alignment"],
        },
        "meeting_types": ["ceo-sync", "exec-meeting", "all-hands", "strategy"],
        "data_access": ["All company data", "Financial summaries", "Project status", "Client relationships"],
    },
    "cfo": {
        "how_it_works": """The CFO agent manages financial strategy and analysis. In meetings, the CFO:

1. **Analyzes Financials** - Reviews invoices, payments, and revenue data from finances.json
2. **Pricing Guidance** - Provides recommendations based on market and cost analysis
3. **Budget Planning** - Helps forecast expenses and revenue
4. **Risk Assessment** - Evaluates financial implications of business decisions""",
        "collaboration": {
            "reports_to": "CEO",
            "direct_reports": [],
            "collaborates_with": ["Sales (pricing)", "PM (budgets)", "Legal (contracts)"],
        },
        "meeting_types": ["exec-meeting", "1on1", "strategy"],
        "data_access": ["Finances data", "Invoice history", "Payment records", "Revenue projections"],
    },
    "cito": {
        "how_it_works": """The CITO (Chief Information Technology Officer) agent guides technical strategy. In meetings, the CITO:

1. **Evaluates Technology** - Assesses technical feasibility and architecture options
2. **Reviews Ideas** - Provides technical perspective on new app submissions
3. **Sets Standards** - Establishes coding practices and technology choices
4. **Mentors Tech Team** - Guides DevLead, DesignLead, and QALead""",
        "collaboration": {
            "reports_to": "CEO",
            "direct_reports": ["DevLead", "DesignLead", "QALead"],
            "collaborates_with": ["PM (technical planning)", "Sales (technical sales support)"],
        },
        "meeting_types": ["tech-meeting", "exec-meeting", "idea-review", "1on1"],
        "data_access": ["Projects data", "Technical decisions", "Architecture docs"],
    },
    "sales": {
        "how_it_works": """The Sales agent handles business development and client acquisition. In meetings, Sales:

1. **Manages Pipeline** - Tracks potential clients and deal stages
2. **Proposal Support** - Helps craft pitches and proposals
3. **Relationship Building** - Strategizes on client relationships
4. **Market Intelligence** - Provides insights on competitors and opportunities""",
        "collaboration": {
            "reports_to": "CEO",
            "direct_reports": [],
            "collaborates_with": ["CFO (pricing)", "PM (scoping)", "Marketing (lead gen)"],
        },
        "meeting_types": ["exec-meeting", "1on1", "strategy"],
        "data_access": ["Clients data", "Ideas pipeline", "Project history"],
    },
    "legal": {
        "how_it_works": """The Legal agent provides guidance on contracts and compliance. In meetings, Legal:

1. **Contract Review** - Analyzes terms and identifies risks
2. **Compliance Guidance** - Advises on data privacy, IP, and regulations
3. **Risk Assessment** - Evaluates legal implications of business decisions
4. **Template Creation** - Helps draft standard agreements""",
        "collaboration": {
            "reports_to": "CEO",
            "direct_reports": [],
            "collaborates_with": ["CFO (contract terms)", "Sales (deal review)", "PM (client agreements)"],
        },
        "meeting_types": ["exec-meeting", "1on1", "idea-review"],
        "data_access": ["Client contracts", "Project agreements", "Compliance docs"],
    },
    "dev_lead": {
        "how_it_works": """The Development Lead agent manages technical implementation. In meetings, DevLead:

1. **Architecture Design** - Creates technical blueprints for projects
2. **Code Review** - Establishes quality standards and best practices
3. **Sprint Planning** - Breaks down work into manageable tasks
4. **Technical Debt** - Identifies and prioritizes tech debt resolution""",
        "collaboration": {
            "reports_to": "CITO",
            "direct_reports": [],
            "collaborates_with": ["DesignLead (implementation)", "QALead (testing)", "PM (scheduling)"],
        },
        "meeting_types": ["tech-meeting", "project-meeting", "1on1", "standup"],
        "data_access": ["Projects data", "Technical specs", "Sprint backlogs"],
    },
    "design_lead": {
        "how_it_works": """The Design Lead agent manages UI/UX and visual design. In meetings, DesignLead:

1. **UX Strategy** - Defines user experience patterns and flows
2. **Design Systems** - Maintains consistent visual language
3. **User Research** - Interprets user feedback into design improvements
4. **Prototype Review** - Evaluates designs against requirements""",
        "collaboration": {
            "reports_to": "CITO",
            "direct_reports": [],
            "collaborates_with": ["DevLead (implementation)", "QALead (usability)", "PM (requirements)"],
        },
        "meeting_types": ["tech-meeting", "project-meeting", "1on1", "idea-review"],
        "data_access": ["Projects data", "Design specs", "User feedback"],
    },
    "qa_lead": {
        "how_it_works": """The QA Lead agent manages quality assurance and testing. In meetings, QALead:

1. **Test Strategy** - Defines testing approaches for each project
2. **Bug Triage** - Prioritizes and categorizes reported issues
3. **Release Certification** - Validates builds before deployment
4. **Tester Coordination** - Works with beta tester program""",
        "collaboration": {
            "reports_to": "CITO",
            "direct_reports": [],
            "collaborates_with": ["DevLead (bug fixes)", "Support (user issues)", "PM (release planning)"],
        },
        "meeting_types": ["tech-meeting", "project-meeting", "1on1", "standup"],
        "data_access": ["Projects data", "Testers data", "Bug reports", "Test results"],
    },
    "pm": {
        "how_it_works": """The Project Manager agent coordinates project delivery. In meetings, PM:

1. **Project Planning** - Creates timelines and milestones
2. **Resource Allocation** - Balances team capacity across projects
3. **Stakeholder Communication** - Bridges client and team needs
4. **Risk Management** - Identifies and mitigates project risks""",
        "collaboration": {
            "reports_to": "CEO",
            "direct_reports": ["CustomerSuccess", "Support"],
            "collaborates_with": ["DevLead (scheduling)", "Clients (communication)", "CFO (budgets)"],
        },
        "meeting_types": ["project-meeting", "exec-meeting", "1on1", "standup", "retro"],
        "data_access": ["Projects data", "Clients data", "Team schedules", "Milestones"],
    },
    "customer_success": {
        "how_it_works": """The Customer Success agent manages post-sale client relationships. In meetings, CustomerSuccess:

1. **Onboarding** - Ensures smooth client transitions after project launch
2. **Health Monitoring** - Tracks client satisfaction and engagement
3. **Expansion Opportunities** - Identifies upsell and cross-sell potential
4. **Retention Strategy** - Develops approaches to maintain long-term relationships""",
        "collaboration": {
            "reports_to": "PM",
            "direct_reports": [],
            "collaborates_with": ["Sales (handoffs)", "Support (escalations)", "Marketing (testimonials)"],
        },
        "meeting_types": ["1on1", "project-meeting"],
        "data_access": ["Clients data", "Projects data", "Support tickets", "Feedback"],
    },
    "marketing": {
        "how_it_works": """The Marketing agent manages brand and growth strategies. In meetings, Marketing:

1. **Brand Strategy** - Maintains consistent messaging and positioning
2. **Content Planning** - Develops content calendars and campaigns
3. **ASO/SEO** - Optimizes app store and search presence
4. **Lead Generation** - Creates strategies to attract potential clients""",
        "collaboration": {
            "reports_to": "CEO",
            "direct_reports": [],
            "collaborates_with": ["Sales (lead handoff)", "CustomerSuccess (case studies)", "DesignLead (brand assets)"],
        },
        "meeting_types": ["exec-meeting", "1on1", "strategy"],
        "data_access": ["Marketing metrics", "Client testimonials", "Campaign data"],
    },
    "support": {
        "how_it_works": """The Support Lead agent manages customer service operations. In meetings, Support:

1. **Ticket Triage** - Categorizes and prioritizes support requests
2. **Knowledge Base** - Maintains documentation and FAQs
3. **Escalation Management** - Routes complex issues appropriately
4. **Tester Program** - Coordinates with beta testers for feedback""",
        "collaboration": {
            "reports_to": "PM",
            "direct_reports": [],
            "collaborates_with": ["QALead (bug reports)", "DevLead (technical issues)", "CustomerSuccess (escalations)"],
        },
        "meeting_types": ["1on1", "standup", "project-meeting"],
        "data_access": ["Support tickets", "Testers data", "Knowledge base", "Bug reports"],
    },
}


# =============================================================================
# AGENT CUSTOMIZATIONS STORE
# =============================================================================

class AgentCustomizationsStore:
    """Store for agent-specific customizations."""

    def __init__(self):
        self.file_path = DATA_DIR / "agent_customizations.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure the customizations file exists."""
        if not self.file_path.exists():
            self._save({})

    def _load(self) -> dict[str, Any]:
        """Load all customizations."""
        content = self.file_path.read_text(encoding="utf-8")
        if not content.strip():
            return {}
        return json.loads(content)

    def _save(self, data: dict[str, Any]) -> None:
        """Save customizations."""
        self.file_path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8"
        )

    def get_agent_defaults(self, agent_id: str) -> dict[str, Any]:
        """Get default values for an agent based on AGENT_INFO."""
        from webapp.app import AGENT_INFO
        agent_info = AGENT_INFO.get(agent_id, {})
        return {
            "display_name": agent_info.get("name", agent_id.replace("_", " ").title()),
            "role_title": agent_info.get("role", agent_id.upper()),
            "description": agent_info.get("description", ""),
            "responsibilities": agent_info.get("responsibilities", []),
            "metrics": agent_info.get("metrics", []),
            "custom_instructions": "",
            "is_active": True,
        }

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        """Get customizations for a specific agent, merged with defaults."""
        all_data = self._load()
        agent_data = all_data.get(agent_id, {})

        # Get defaults and merge with customizations
        defaults = self.get_agent_defaults(agent_id)
        merged = {**defaults, **agent_data}

        # Add documentation
        merged["documentation"] = AGENT_DOCUMENTATION.get(agent_id, {})

        return merged

    def update_agent(self, agent_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update customizations for a specific agent."""
        all_data = self._load()

        if agent_id not in all_data:
            all_data[agent_id] = {}

        # Only store non-default values
        all_data[agent_id].update(updates)
        all_data[agent_id]["updated_at"] = datetime.now().isoformat()

        self._save(all_data)
        return self.get_agent(agent_id)

    def reset_agent(self, agent_id: str) -> dict[str, Any]:
        """Reset an agent to defaults."""
        all_data = self._load()
        if agent_id in all_data:
            del all_data[agent_id]
            self._save(all_data)
        return self.get_agent(agent_id)

    def get_all_agents(self) -> dict[str, dict[str, Any]]:
        """Get all agents with their customizations."""
        from webapp.app import AGENT_INFO
        result = {}
        for agent_id in AGENT_INFO.keys():
            result[agent_id] = self.get_agent(agent_id)
        return result

    def has_customizations(self, agent_id: str) -> bool:
        """Check if an agent has any customizations."""
        all_data = self._load()
        return agent_id in all_data and bool(all_data[agent_id])


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
_settings_store: SettingsStore | None = None
_agent_customizations_store: AgentCustomizationsStore | None = None


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


def get_settings_store() -> SettingsStore:
    """Get the settings store singleton."""
    global _settings_store
    if _settings_store is None:
        _settings_store = SettingsStore()
    return _settings_store


def get_agent_customizations_store() -> AgentCustomizationsStore:
    """Get the agent customizations store singleton."""
    global _agent_customizations_store
    if _agent_customizations_store is None:
        _agent_customizations_store = AgentCustomizationsStore()
    return _agent_customizations_store
