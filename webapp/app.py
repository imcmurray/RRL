"""
Rinse Repeat Labs — Web Dashboard

A Flask web application for managing the company through a browser interface.
"""

import sys
from pathlib import Path
from datetime import datetime
from functools import wraps

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
from src.utils import query_decisions, list_meetings, load_file
import config

app = Flask(__name__)
app.secret_key = "rinse-repeat-labs-secret-key-change-in-production"


# =============================================================================
# TEMPLATE FILTERS
# =============================================================================

@app.template_filter('datetime')
def format_datetime(value):
    """Format ISO datetime string."""
    if not value:
        return ""
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return value[:16] if value else ""


@app.template_filter('date')
def format_date(value):
    """Format ISO datetime string as date."""
    if not value:
        return ""
    try:
        return value[:10]
    except:
        return value


@app.template_filter('currency')
def format_currency(value):
    """Format number as currency."""
    try:
        return f"${float(value):,.2f}"
    except:
        return "$0.00"


@app.template_filter('status_badge')
def status_badge(status):
    """Return Bootstrap badge class for status."""
    badges = {
        # Ideas
        'submitted': 'warning',
        'under_review': 'info',
        'approved': 'success',
        'rejected': 'danger',
        'in_development': 'primary',
        'completed': 'secondary',
        'on_hold': 'dark',
        # Testers
        'applied': 'warning',
        'active': 'success',
        'inactive': 'secondary',
        # Projects
        'planning': 'warning',
        'design': 'info',
        'development': 'primary',
        'qa': 'info',
        'launch': 'success',
        'maintenance': 'secondary',
        # Invoices
        'draft': 'secondary',
        'sent': 'info',
        'paid': 'success',
        'overdue': 'danger',
        'cancelled': 'dark',
    }
    return badges.get(status, 'secondary')


# =============================================================================
# DASHBOARD
# =============================================================================

@app.route('/')
def dashboard():
    """Main dashboard view."""
    ideas_store = get_ideas_store()
    testers_store = get_testers_store()
    clients_store = get_clients_store()
    projects_store = get_projects_store()
    finances_store = get_finances_store()

    # Get counts
    all_ideas = ideas_store.get_all()
    all_testers = testers_store.get_all()
    all_clients = clients_store.get_all()
    all_projects = projects_store.get_all()

    # Sort by created_at descending for recent items
    all_ideas_sorted = sorted(all_ideas, key=lambda x: x.get('created_at', ''), reverse=True)
    all_testers_sorted = sorted(all_testers, key=lambda x: x.get('created_at', ''), reverse=True)

    # Ideas by status
    ideas_pending = len([i for i in all_ideas if i.get('status') == 'submitted'])
    ideas_review = len([i for i in all_ideas if i.get('status') == 'under_review'])
    ideas_approved = len([i for i in all_ideas if i.get('status') == 'approved'])

    # Testers by status
    testers_pending = len([t for t in all_testers if t.get('status') == 'applied'])
    testers_active = len([t for t in all_testers if t.get('status') in ['active', 'approved']])

    # Active projects
    active_projects = projects_store.get_active()

    # Outstanding invoices
    invoices = finances_store.get_invoices()
    outstanding = sum(i.get('amount', 0) for i in invoices
                     if i.get('status') in ['sent', 'overdue'])

    # Recent decisions
    recent_decisions = query_decisions(limit=5)

    # Recent meetings
    recent_meetings = list_meetings(limit=5)

    return render_template('dashboard.html',
        ideas_count=len(all_ideas),
        ideas_pending=ideas_pending,
        ideas_review=ideas_review,
        ideas_approved=ideas_approved,
        testers_count=len(all_testers),
        testers_pending=testers_pending,
        testers_active=testers_active,
        clients_count=len(all_clients),
        projects_count=len(all_projects),
        active_projects=active_projects,
        outstanding_amount=outstanding,
        recent_decisions=recent_decisions,
        recent_meetings=recent_meetings,
        recent_ideas=all_ideas_sorted[:5],
        recent_testers=all_testers_sorted[:5],
    )


# =============================================================================
# IDEAS
# =============================================================================

@app.route('/ideas')
def ideas_list():
    """List all ideas."""
    store = get_ideas_store()
    status_filter = request.args.get('status', '')

    if status_filter:
        ideas = store.query(status=status_filter)
    else:
        ideas = store.get_all()

    # Sort by created_at descending
    ideas = sorted(ideas, key=lambda x: x.get('created_at', ''), reverse=True)

    return render_template('ideas/list.html',
        ideas=ideas,
        statuses=IdeaStatus,
        current_status=status_filter
    )


@app.route('/ideas/new', methods=['GET', 'POST'])
def ideas_new():
    """Create a new idea."""
    if request.method == 'POST':
        store = get_ideas_store()

        platforms = request.form.getlist('platforms')
        features = [f.strip() for f in request.form.get('features', '').split('\n') if f.strip()]

        idea = store.create_idea(
            name=request.form.get('name'),
            description=request.form.get('description'),
            submitter_name=request.form.get('submitter_name'),
            submitter_email=request.form.get('submitter_email'),
            submitter_company=request.form.get('submitter_company', ''),
            platforms=platforms,
            revenue_model=request.form.get('revenue_model', ''),
            timeline=request.form.get('timeline', ''),
            budget_range=request.form.get('budget_range', ''),
            features=features,
            competitors=request.form.get('competitors', ''),
            differentiation=request.form.get('differentiation', ''),
        )

        flash(f'Idea "{idea["name"]}" created successfully!', 'success')
        return redirect(url_for('ideas_detail', idea_id=idea['id']))

    return render_template('ideas/form.html', idea=None)


@app.route('/ideas/<idea_id>')
def ideas_detail(idea_id):
    """View idea details."""
    store = get_ideas_store()
    idea = store.get_by_id(idea_id)

    if not idea:
        flash('Idea not found', 'error')
        return redirect(url_for('ideas_list'))

    return render_template('ideas/detail.html', idea=idea, statuses=IdeaStatus)


@app.route('/ideas/<idea_id>/status', methods=['POST'])
def ideas_update_status(idea_id):
    """Update idea status."""
    store = get_ideas_store()
    new_status = request.form.get('status')
    note = request.form.get('note', '')

    result = store.update_status(idea_id, IdeaStatus(new_status), note)

    if result:
        flash(f'Status updated to {new_status}', 'success')
    else:
        flash('Failed to update status', 'error')

    return redirect(url_for('ideas_detail', idea_id=idea_id))


@app.route('/ideas/<idea_id>/note', methods=['POST'])
def ideas_add_note(idea_id):
    """Add a note to an idea."""
    store = get_ideas_store()
    note = request.form.get('note')
    author = request.form.get('author', 'Architect')

    store.add_note(idea_id, note, author)
    flash('Note added', 'success')

    return redirect(url_for('ideas_detail', idea_id=idea_id))


@app.route('/ideas/<idea_id>/edit', methods=['GET', 'POST'])
def ideas_edit(idea_id):
    """Edit an existing idea."""
    store = get_ideas_store()
    idea = store.get_by_id(idea_id)

    if not idea:
        flash('Idea not found', 'error')
        return redirect(url_for('ideas_list'))

    if request.method == 'POST':
        platforms = request.form.getlist('platforms')
        features = [f.strip() for f in request.form.get('features', '').split('\n') if f.strip()]

        store.update(idea_id, {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'submitter_name': request.form.get('submitter_name'),
            'submitter_email': request.form.get('submitter_email'),
            'submitter_phone': request.form.get('submitter_phone', ''),
            'platforms': platforms,
            'revenue_model': request.form.get('revenue_model', ''),
            'timeline': request.form.get('timeline', ''),
            'budget': float(request.form.get('budget', 0)) if request.form.get('budget') else None,
            'features': features,
            'problem_statement': request.form.get('problem_statement', ''),
            'proposed_solution': request.form.get('proposed_solution', ''),
            'target_audience': request.form.get('target_audience', ''),
        })

        flash(f'Idea "{idea["name"]}" updated!', 'success')
        return redirect(url_for('ideas_detail', idea_id=idea_id))

    return render_template('ideas/form.html', idea=idea)


@app.route('/ideas/create', methods=['POST'])
def ideas_create():
    """Create a new idea (form POST handler)."""
    store = get_ideas_store()

    platforms = request.form.getlist('platforms')
    features = [f.strip() for f in request.form.get('features', '').split('\n') if f.strip()]

    idea = store.create_idea(
        name=request.form.get('name'),
        description=request.form.get('description'),
        submitter_name=request.form.get('submitter_name'),
        submitter_email=request.form.get('submitter_email'),
        submitter_company=request.form.get('submitter_company', ''),
        platforms=platforms,
        revenue_model=request.form.get('revenue_model', ''),
        timeline=request.form.get('timeline', ''),
        budget_range=request.form.get('budget', ''),
        features=features,
        competitors=request.form.get('competitors', ''),
        differentiation=request.form.get('differentiation', ''),
    )

    flash(f'Idea "{idea["name"]}" created successfully!', 'success')
    return redirect(url_for('ideas_detail', idea_id=idea['id']))


@app.route('/ideas/<idea_id>/delete', methods=['POST'])
def ideas_delete(idea_id):
    """Delete an idea."""
    store = get_ideas_store()
    result = store.delete(idea_id)

    if result:
        flash('Idea deleted', 'success')
    else:
        flash('Failed to delete idea', 'error')

    return redirect(url_for('ideas_list'))


@app.route('/ideas/<idea_id>/review')
def ideas_review(idea_id):
    """Review form for an idea."""
    store = get_ideas_store()
    idea = store.get_by_id(idea_id)

    if not idea:
        flash('Idea not found', 'error')
        return redirect(url_for('ideas_list'))

    return render_template('ideas/review.html', idea=idea)


@app.route('/ideas/<idea_id>/review', methods=['POST'])
def ideas_submit_review(idea_id):
    """Submit a review decision for an idea."""
    store = get_ideas_store()
    decision = request.form.get('decision')
    review_notes = request.form.get('review_notes', '')
    concerns = request.form.get('concerns', '')
    suggestions = request.form.get('suggestions', '')

    # Update status based on decision
    store.update_status(idea_id, IdeaStatus(decision), review_notes)

    # Add review notes
    if concerns:
        store.add_note(idea_id, f"Concerns: {concerns}", "Review")
    if suggestions:
        store.add_note(idea_id, f"Suggestions: {suggestions}", "Review")

    flash(f'Idea {decision}!', 'success')
    return redirect(url_for('ideas_detail', idea_id=idea_id))


# =============================================================================
# TESTERS
# =============================================================================

@app.route('/testers')
def testers_list():
    """List all testers."""
    store = get_testers_store()
    status_filter = request.args.get('status', '')
    device_filter = request.args.get('device', '')

    if device_filter:
        testers = store.get_by_device_type(device_filter)
    elif status_filter:
        testers = store.query(status=status_filter)
    else:
        testers = store.get_all()

    return render_template('testers/list.html',
        testers=testers,
        statuses=TesterStatus,
        current_status=status_filter,
        current_device=device_filter
    )


@app.route('/testers/new', methods=['GET', 'POST'])
def testers_new():
    """Create a new tester."""
    if request.method == 'POST':
        store = get_testers_store()

        # Parse devices
        devices = []
        device_types = request.form.getlist('device_type')
        device_models = request.form.getlist('device_model')
        device_os = request.form.getlist('device_os')

        for i in range(len(device_types)):
            if device_types[i]:
                devices.append({
                    'type': device_types[i],
                    'model': device_models[i] if i < len(device_models) else '',
                    'os': device_os[i] if i < len(device_os) else '',
                })

        languages = [l.strip() for l in request.form.get('languages', 'English').split(',')]

        tester = store.create_tester(
            name=request.form.get('name'),
            email=request.form.get('email'),
            devices=devices,
            experience_level=request.form.get('experience_level', 'some'),
            hours_per_week=int(request.form.get('hours_per_week', 5)),
            payment_method=request.form.get('payment_method', 'paypal'),
            payment_details=request.form.get('payment_details'),
            location=request.form.get('location', ''),
            languages=languages,
        )

        flash(f'Tester "{tester["name"]}" created successfully!', 'success')
        return redirect(url_for('testers_detail', tester_id=tester['id']))

    return render_template('testers/form.html', tester=None)


@app.route('/testers/<tester_id>')
def testers_detail(tester_id):
    """View tester details."""
    store = get_testers_store()
    projects_store = get_projects_store()

    tester = store.get_by_id(tester_id)

    if not tester:
        flash('Tester not found', 'error')
        return redirect(url_for('testers_list'))

    # Get assigned projects
    assigned_projects = []
    for proj_id in tester.get('projects', []):
        proj = projects_store.get_by_id(proj_id)
        if proj:
            assigned_projects.append(proj)

    return render_template('testers/detail.html',
        tester=tester,
        assigned_projects=assigned_projects,
        statuses=TesterStatus
    )


@app.route('/testers/<tester_id>/approve', methods=['POST'])
def testers_approve(tester_id):
    """Approve a tester."""
    store = get_testers_store()
    note = request.form.get('note', '')

    result = store.approve(tester_id, note)

    if result:
        flash('Tester approved!', 'success')
    else:
        flash('Failed to approve tester', 'error')

    return redirect(url_for('testers_detail', tester_id=tester_id))


@app.route('/testers/<tester_id>/reject', methods=['POST'])
def testers_reject(tester_id):
    """Reject a tester."""
    store = get_testers_store()
    reason = request.form.get('reason', 'No reason provided')

    result = store.reject(tester_id, reason)

    if result:
        flash('Tester rejected', 'warning')
    else:
        flash('Failed to reject tester', 'error')

    return redirect(url_for('testers_detail', tester_id=tester_id))


@app.route('/testers/<tester_id>/edit', methods=['GET', 'POST'])
def testers_edit(tester_id):
    """Edit a tester."""
    store = get_testers_store()
    tester = store.get_by_id(tester_id)

    if not tester:
        flash('Tester not found', 'error')
        return redirect(url_for('testers_list'))

    if request.method == 'POST':
        devices = [d.strip() for d in request.form.get('devices', '').split('\n') if d.strip()]
        skills = [s.strip() for s in request.form.get('skills', '').split('\n') if s.strip()]

        store.update(tester_id, {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone', ''),
            'location': request.form.get('location', ''),
            'timezone': request.form.get('timezone', ''),
            'devices': devices,
            'skills': skills,
            'experience_level': request.form.get('experience_level', ''),
            'hours_per_week': int(request.form.get('hours_per_week', 5)) if request.form.get('hours_per_week') else 5,
            'payment_method': request.form.get('payment_method', ''),
            'payment_details': request.form.get('payment_details', ''),
        })

        flash(f'Tester "{tester["name"]}" updated!', 'success')
        return redirect(url_for('testers_detail', tester_id=tester_id))

    return render_template('testers/form.html', tester=tester)


@app.route('/testers/create', methods=['POST'])
def testers_create():
    """Create a new tester."""
    store = get_testers_store()

    devices = [d.strip() for d in request.form.get('devices', '').split('\n') if d.strip()]
    skills = [s.strip() for s in request.form.get('skills', '').split('\n') if s.strip()]

    tester = store.create_tester(
        name=request.form.get('name'),
        email=request.form.get('email'),
        devices=devices,
        experience_level=request.form.get('experience_level', 'some'),
        hours_per_week=int(request.form.get('hours_per_week', 5)) if request.form.get('hours_per_week') else 5,
        payment_method=request.form.get('payment_method', 'paypal'),
        payment_details=request.form.get('payment_details'),
        location=request.form.get('location', ''),
        languages=['English'],
    )

    # Add skills if provided
    if skills:
        store.update(tester['id'], {'skills': skills})

    flash(f'Tester "{tester["name"]}" created successfully!', 'success')
    return redirect(url_for('testers_detail', tester_id=tester['id']))


@app.route('/testers/<tester_id>/note', methods=['POST'])
def testers_add_note(tester_id):
    """Add a note to a tester."""
    store = get_testers_store()
    note = request.form.get('note')
    author = request.form.get('author', 'Dashboard')

    store.add_note(tester_id, note, author)
    flash('Note added', 'success')

    return redirect(url_for('testers_detail', tester_id=tester_id))


@app.route('/testers/<tester_id>/delete', methods=['POST'])
def testers_delete(tester_id):
    """Delete a tester."""
    store = get_testers_store()
    result = store.delete(tester_id)

    if result:
        flash('Tester deleted', 'success')
    else:
        flash('Failed to delete tester', 'error')

    return redirect(url_for('testers_list'))


@app.route('/testers/<tester_id>/status', methods=['POST'])
def testers_update_status(tester_id):
    """Update tester status."""
    store = get_testers_store()
    new_status = request.form.get('status')

    store.update(tester_id, {'status': new_status})
    flash(f'Status updated to {new_status}', 'success')

    return redirect(url_for('testers_detail', tester_id=tester_id))


@app.route('/testers/<tester_id>/assign')
def testers_assign(tester_id):
    """Assign tester to project page."""
    store = get_testers_store()
    projects_store = get_projects_store()

    tester = store.get_by_id(tester_id)
    if not tester:
        flash('Tester not found', 'error')
        return redirect(url_for('testers_list'))

    projects = projects_store.get_active()

    return render_template('testers/assign.html', tester=tester, projects=projects)


# =============================================================================
# CLIENTS
# =============================================================================

@app.route('/clients')
def clients_list():
    """List all clients."""
    store = get_clients_store()
    clients = store.get_all()

    return render_template('clients/list.html', clients=clients)


@app.route('/clients/new', methods=['GET', 'POST'])
def clients_new():
    """Create a new client."""
    if request.method == 'POST':
        store = get_clients_store()

        client = store.create_client(
            name=request.form.get('name'),
            company=request.form.get('company'),
            email=request.form.get('email'),
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            billing_email=request.form.get('billing_email', ''),
            primary_contact=request.form.get('primary_contact', ''),
            source=request.form.get('source', ''),
        )

        flash(f'Client "{client["company"]}" created successfully!', 'success')
        return redirect(url_for('clients_detail', client_id=client['id']))

    return render_template('clients/form.html', client=None)


@app.route('/clients/<client_id>')
def clients_detail(client_id):
    """View client details."""
    clients_store = get_clients_store()
    projects_store = get_projects_store()
    ideas_store = get_ideas_store()
    finances_store = get_finances_store()

    client = clients_store.get_by_id(client_id)

    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('clients_list'))

    # Get related data
    projects = [projects_store.get_by_id(pid) for pid in client.get('projects', [])]
    projects = [p for p in projects if p]

    ideas = [ideas_store.get_by_id(iid) for iid in client.get('ideas', [])]
    ideas = [i for i in ideas if i]

    invoices = finances_store.query(type='invoice', client_id=client_id)

    return render_template('clients/detail.html',
        client=client,
        projects=projects,
        ideas=ideas,
        invoices=invoices
    )


@app.route('/clients/<client_id>/edit', methods=['GET', 'POST'])
def clients_edit(client_id):
    """Edit a client."""
    store = get_clients_store()
    client = store.get_by_id(client_id)

    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('clients_list'))

    if request.method == 'POST':
        store.update(client_id, {
            'company_name': request.form.get('company_name'),
            'contact_name': request.form.get('contact_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone', ''),
            'website': request.form.get('website', ''),
            'industry': request.form.get('industry', ''),
            'address': request.form.get('address', ''),
            'contact_title': request.form.get('contact_title', ''),
        })

        flash(f'Client updated!', 'success')
        return redirect(url_for('clients_detail', client_id=client_id))

    return render_template('clients/form.html', client=client)


@app.route('/clients/create', methods=['POST'])
def clients_create():
    """Create a new client."""
    store = get_clients_store()

    client = store.create_client(
        name=request.form.get('contact_name'),
        company=request.form.get('company_name'),
        email=request.form.get('email'),
        phone=request.form.get('phone', ''),
        address=request.form.get('address', ''),
        billing_email=request.form.get('email', ''),
        primary_contact=request.form.get('contact_name', ''),
        source='Dashboard',
    )

    # Update with additional fields
    store.update(client['id'], {
        'company_name': request.form.get('company_name'),
        'contact_name': request.form.get('contact_name'),
        'website': request.form.get('website', ''),
        'industry': request.form.get('industry', ''),
        'contact_title': request.form.get('contact_title', ''),
    })

    flash(f'Client created successfully!', 'success')
    return redirect(url_for('clients_detail', client_id=client['id']))


@app.route('/clients/<client_id>/note', methods=['POST'])
def clients_add_note(client_id):
    """Add a note to a client."""
    store = get_clients_store()
    note = request.form.get('note')
    author = request.form.get('author', 'Dashboard')

    store.add_note(client_id, note, author)
    flash('Note added', 'success')

    return redirect(url_for('clients_detail', client_id=client_id))


@app.route('/clients/<client_id>/delete', methods=['POST'])
def clients_delete(client_id):
    """Delete a client."""
    store = get_clients_store()
    result = store.delete(client_id)

    if result:
        flash('Client deleted', 'success')
    else:
        flash('Failed to delete client', 'error')

    return redirect(url_for('clients_list'))


# =============================================================================
# PROJECTS
# =============================================================================

@app.route('/projects')
def projects_list():
    """List all projects."""
    store = get_projects_store()
    clients_store = get_clients_store()

    status_filter = request.args.get('status', '')
    show_active = request.args.get('active', '')

    if show_active:
        projects = store.get_active()
    elif status_filter:
        projects = store.query(status=status_filter)
    else:
        projects = store.get_all()

    # Enrich with client info
    for project in projects:
        client = clients_store.get_by_id(project.get('client_id', ''))
        project['_client'] = client

    return render_template('projects/list.html',
        projects=projects,
        statuses=ProjectStatus,
        current_status=status_filter,
        show_active=show_active
    )


@app.route('/projects/new', methods=['GET', 'POST'])
def projects_new():
    """Create a new project."""
    clients_store = get_clients_store()
    ideas_store = get_ideas_store()

    if request.method == 'POST':
        store = get_projects_store()

        platforms = request.form.getlist('platforms')
        tech_stack = [t.strip() for t in request.form.get('tech_stack', '').split(',') if t.strip()]
        team = request.form.getlist('team')

        project = store.create_project(
            name=request.form.get('name'),
            client_id=request.form.get('client_id'),
            idea_id=request.form.get('idea_id', ''),
            description=request.form.get('description', ''),
            platforms=platforms,
            tech_stack=tech_stack,
            revenue_model=request.form.get('revenue_model', ''),
            contract_value=float(request.form.get('contract_value', 0) or 0),
            start_date=request.form.get('start_date', ''),
            target_launch=request.form.get('target_launch', ''),
            team=team or ['pm', 'dev_lead', 'design_lead', 'qa_lead'],
        )

        # Link to client
        clients_store.link_project(project['client_id'], project['id'])

        flash(f'Project "{project["name"]}" created successfully!', 'success')
        return redirect(url_for('projects_detail', project_id=project['id']))

    clients = clients_store.get_all()
    ideas = ideas_store.query(status='approved')

    return render_template('projects/form.html',
        project=None,
        clients=clients,
        ideas=ideas,
        agents=config.ALL_AGENTS
    )


@app.route('/projects/<project_id>')
def projects_detail(project_id):
    """View project details."""
    store = get_projects_store()
    clients_store = get_clients_store()
    testers_store = get_testers_store()

    project = store.get_by_id(project_id)

    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects_list'))

    client = clients_store.get_by_id(project.get('client_id', ''))

    # Get assigned testers
    testers = [testers_store.get_by_id(tid) for tid in project.get('testers', [])]
    testers = [t for t in testers if t]

    return render_template('projects/detail.html',
        project=project,
        client=client,
        testers=testers,
        statuses=ProjectStatus
    )


@app.route('/projects/<project_id>/status', methods=['POST'])
def projects_update_status(project_id):
    """Update project status."""
    store = get_projects_store()
    new_status = request.form.get('status')
    note = request.form.get('note', '')

    result = store.update_status(project_id, ProjectStatus(new_status), note)

    if result:
        flash(f'Status updated to {new_status}', 'success')
    else:
        flash('Failed to update status', 'error')

    return redirect(url_for('projects_detail', project_id=project_id))


@app.route('/projects/<project_id>/edit', methods=['GET', 'POST'])
def projects_edit(project_id):
    """Edit a project."""
    store = get_projects_store()
    clients_store = get_clients_store()

    project = store.get_by_id(project_id)

    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects_list'))

    if request.method == 'POST':
        platforms = request.form.getlist('platforms')

        store.update(project_id, {
            'name': request.form.get('name'),
            'description': request.form.get('description', ''),
            'client_id': request.form.get('client_id'),
            'platforms': platforms,
            'status': request.form.get('status', project.get('status')),
            'start_date': request.form.get('start_date', ''),
            'target_date': request.form.get('target_date', ''),
            'budget': float(request.form.get('budget', 0)) if request.form.get('budget') else None,
            'value': float(request.form.get('value', 0)) if request.form.get('value') else None,
        })

        flash(f'Project updated!', 'success')
        return redirect(url_for('projects_detail', project_id=project_id))

    clients = clients_store.get_all()
    return render_template('projects/form.html', project=project, clients=clients, ideas=[], agents=config.ALL_AGENTS)


@app.route('/projects/create', methods=['POST'])
def projects_create():
    """Create a new project."""
    store = get_projects_store()
    clients_store = get_clients_store()

    platforms = request.form.getlist('platforms')

    project = store.create_project(
        name=request.form.get('name'),
        client_id=request.form.get('client_id'),
        idea_id=request.form.get('idea_id', ''),
        description=request.form.get('description', ''),
        platforms=platforms,
        tech_stack=[],
        revenue_model='',
        contract_value=float(request.form.get('value', 0) or 0),
        start_date=request.form.get('start_date', ''),
        target_launch=request.form.get('target_date', ''),
        team=['pm', 'dev_lead', 'design_lead', 'qa_lead'],
    )

    # Update with additional fields
    store.update(project['id'], {
        'budget': float(request.form.get('budget', 0)) if request.form.get('budget') else None,
        'status': request.form.get('status', 'planning'),
    })

    # Link to client
    if project.get('client_id'):
        clients_store.link_project(project['client_id'], project['id'])

    flash(f'Project "{project["name"]}" created!', 'success')
    return redirect(url_for('projects_detail', project_id=project['id']))


@app.route('/projects/<project_id>/note', methods=['POST'])
def projects_add_note(project_id):
    """Add a note to a project."""
    store = get_projects_store()
    note = request.form.get('note')
    author = request.form.get('author', 'Dashboard')

    store.add_note(project_id, note, author)
    flash('Note added', 'success')

    return redirect(url_for('projects_detail', project_id=project_id))


@app.route('/projects/<project_id>/delete', methods=['POST'])
def projects_delete(project_id):
    """Delete a project."""
    store = get_projects_store()
    result = store.delete(project_id)

    if result:
        flash('Project deleted', 'success')
    else:
        flash('Failed to delete project', 'error')

    return redirect(url_for('projects_list'))


# =============================================================================
# FINANCES
# =============================================================================

@app.route('/finances')
def finances_dashboard():
    """Financial dashboard."""
    store = get_finances_store()
    clients_store = get_clients_store()

    invoices = store.get_invoices()
    payments = store.get_payments()

    # Enrich invoices with client info
    for inv in invoices:
        client = clients_store.get_by_id(inv.get('client_id', ''))
        inv['client_name'] = client.get('company_name', client.get('name', '')) if client else ''

    # Calculate totals
    total_invoiced = sum(i.get('amount', 0) for i in invoices)
    total_paid = sum(i.get('amount', 0) for i in invoices if i.get('status') == 'paid')
    total_outstanding = sum(i.get('amount', 0) for i in invoices
                          if i.get('status') in ['sent', 'overdue'])

    return render_template('finances/dashboard.html',
        invoices=invoices[:10],  # Show recent 10
        payments=payments[:5],   # Show recent 5
        total_invoiced=total_invoiced,
        total_paid=total_paid,
        total_outstanding=total_outstanding,
        statuses=InvoiceStatus
    )


@app.route('/finances/invoices/new', methods=['GET', 'POST'])
def finances_new_invoice():
    """Create a new invoice."""
    clients_store = get_clients_store()
    projects_store = get_projects_store()

    if request.method == 'POST':
        store = get_finances_store()

        invoice = store.create_invoice(
            client_id=request.form.get('client_id'),
            project_id=request.form.get('project_id'),
            amount=float(request.form.get('amount', 0)),
            description=request.form.get('description'),
            due_date=request.form.get('due_date'),
        )

        flash(f'Invoice {invoice["invoice_number"]} created!', 'success')
        return redirect(url_for('finances_dashboard'))

    clients = clients_store.get_all()
    projects = projects_store.get_all()

    return render_template('finances/invoice_form.html',
        clients=clients,
        projects=projects
    )


@app.route('/finances/invoices/<invoice_id>/send', methods=['POST'])
def finances_send_invoice(invoice_id):
    """Mark invoice as sent."""
    store = get_finances_store()
    store.mark_invoice_sent(invoice_id)
    flash('Invoice marked as sent', 'success')
    return redirect(url_for('finances_dashboard'))


@app.route('/finances/invoices/<invoice_id>/paid', methods=['POST'])
def finances_mark_paid(invoice_id):
    """Mark invoice as paid."""
    store = get_finances_store()
    finances_store = get_finances_store()
    clients_store = get_clients_store()

    invoice = store.get_by_id(invoice_id)
    if invoice:
        store.mark_invoice_paid(invoice_id)

        # Record payment
        finances_store.record_payment(
            payment_type=PaymentType.CLIENT_PAYMENT,
            amount=invoice.get('amount', 0),
            description=f"Payment for {invoice.get('invoice_number')}",
            reference_id=invoice.get('client_id'),
            project_id=invoice.get('project_id'),
            invoice_id=invoice_id,
        )

        # Update client financials
        clients_store.update_financials(
            invoice.get('client_id'),
            paid=invoice.get('amount', 0)
        )

        flash('Invoice marked as paid', 'success')

    return redirect(url_for('finances_dashboard'))


@app.route('/finances/invoices')
def finances_invoices():
    """List all invoices."""
    store = get_finances_store()
    clients_store = get_clients_store()

    status_filter = request.args.get('status', '')
    invoices = store.get_invoices()

    if status_filter:
        invoices = [i for i in invoices if i.get('status') == status_filter]

    # Enrich with client info
    for inv in invoices:
        client = clients_store.get_by_id(inv.get('client_id', ''))
        inv['client_name'] = client.get('company_name', client.get('name', '')) if client else ''

    return render_template('finances/invoices.html',
        invoices=invoices,
        current_status=status_filter
    )


@app.route('/finances/invoices/<invoice_id>')
def finances_invoice_detail(invoice_id):
    """View invoice details."""
    store = get_finances_store()
    invoice = store.get_by_id(invoice_id)

    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('finances_invoices'))

    return render_template('finances/invoice_detail.html', invoice=invoice)


@app.route('/finances/invoices/<invoice_id>/edit', methods=['GET', 'POST'])
def finances_invoice_edit(invoice_id):
    """Edit an invoice."""
    store = get_finances_store()
    clients_store = get_clients_store()
    projects_store = get_projects_store()

    invoice = store.get_by_id(invoice_id)

    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('finances_invoices'))

    if request.method == 'POST':
        store.update(invoice_id, {
            'client_id': request.form.get('client_id'),
            'project_id': request.form.get('project_id'),
            'amount': float(request.form.get('amount', 0)),
            'description': request.form.get('description', ''),
            'due_date': request.form.get('due_date', ''),
            'status': request.form.get('status', invoice.get('status')),
        })

        flash('Invoice updated!', 'success')
        return redirect(url_for('finances_invoices'))

    clients = clients_store.get_all()
    projects = projects_store.get_all()

    return render_template('finances/invoice_form.html',
        invoice=invoice,
        clients=clients,
        projects=projects
    )


@app.route('/finances/invoices/create', methods=['POST'])
def finances_invoice_create():
    """Create a new invoice."""
    store = get_finances_store()

    invoice = store.create_invoice(
        client_id=request.form.get('client_id'),
        project_id=request.form.get('project_id'),
        amount=float(request.form.get('amount', 0)),
        description=request.form.get('description'),
        due_date=request.form.get('due_date'),
    )

    # Update status if action is send
    if request.form.get('action') == 'send':
        store.mark_invoice_sent(invoice['id'])

    flash(f'Invoice {invoice["invoice_number"]} created!', 'success')
    return redirect(url_for('finances_invoices'))


@app.route('/finances/invoice/new')
def finances_invoice_new():
    """New invoice form."""
    clients_store = get_clients_store()
    projects_store = get_projects_store()

    clients = clients_store.get_all()
    projects = projects_store.get_all()

    return render_template('finances/invoice_form.html',
        invoice=None,
        clients=clients,
        projects=projects
    )


@app.route('/finances/payments')
def finances_payments():
    """List all payments."""
    store = get_finances_store()
    payments = store.get_payments()

    total_income = sum(p.get('amount', 0) for p in payments if p.get('type') == 'income')
    total_expenses = sum(p.get('amount', 0) for p in payments if p.get('type') == 'expense')

    return render_template('finances/payments.html',
        payments=payments,
        total_income=total_income,
        total_expenses=total_expenses
    )


@app.route('/finances/payment/new')
def finances_payment_new():
    """New payment form."""
    store = get_finances_store()
    clients_store = get_clients_store()

    invoices = store.get_invoices()
    invoices = [i for i in invoices if i.get('status') in ['sent', 'overdue']]

    # Enrich with client info
    for inv in invoices:
        client = clients_store.get_by_id(inv.get('client_id', ''))
        inv['client_name'] = client.get('company_name', client.get('name', '')) if client else ''

    clients = clients_store.get_all()

    return render_template('finances/payment_form.html',
        invoices=invoices,
        clients=clients
    )


@app.route('/finances/payment/create', methods=['POST'])
def finances_payment_create():
    """Record a new payment."""
    store = get_finances_store()

    payment_type = request.form.get('type')
    amount = float(request.form.get('amount', 0))

    store.record_payment(
        payment_type=PaymentType.CLIENT_PAYMENT if payment_type == 'income' else PaymentType.EXPENSE,
        amount=amount,
        description=request.form.get('description', ''),
        reference_id=request.form.get('reference', ''),
        invoice_id=request.form.get('invoice_id', ''),
    )

    # If linked to invoice, mark as paid
    invoice_id = request.form.get('invoice_id')
    if invoice_id:
        store.mark_invoice_paid(invoice_id)

    flash('Payment recorded!', 'success')
    return redirect(url_for('finances_payments'))


@app.route('/finances/expense/new')
def finances_expense_new():
    """New expense form."""
    return render_template('finances/payment_form.html',
        invoices=[],
        clients=[],
        expense_mode=True
    )


# =============================================================================
# REPORTS
# =============================================================================

@app.route('/reports')
def reports_list():
    """List available reports."""
    reports_dir = config.BASE_DIR / 'reports'
    report_files = []

    if reports_dir.exists():
        for f in sorted(reports_dir.glob('*.md'), reverse=True):
            report_files.append({
                'name': f.stem,
                'filename': f.name,
                'modified': datetime.fromtimestamp(f.stat().st_mtime)
            })

    return render_template('reports/list.html', reports=report_files[:20])


@app.route('/reports/generate')
def reports_generate():
    """Show report generation form."""
    clients_store = get_clients_store()
    clients = clients_store.get_all()

    return render_template('reports/generate.html', clients=clients)


@app.route('/reports/create', methods=['POST'])
def reports_create():
    """Generate a report from form."""
    report_type = request.form.get('report_type')
    client_id = request.form.get('client_id')

    if report_type == 'ideas':
        content = reports.generate_ideas_pipeline_report()
        title = 'Ideas Pipeline Report'
    elif report_type == 'testers':
        content = reports.generate_tester_program_report()
        title = 'Tester Program Report'
    elif report_type == 'projects':
        content = reports.generate_projects_status_report()
        title = 'Projects Status Report'
    elif report_type == 'finances':
        content = reports.generate_financial_summary_report()
        title = 'Financial Summary Report'
    elif report_type == 'client' and client_id:
        content = reports.generate_client_report(client_id)
        title = 'Client Report'
    elif report_type == 'comprehensive':
        # Generate comprehensive report
        content = "# Comprehensive Company Report\n\n"
        content += reports.generate_ideas_pipeline_report() + "\n\n---\n\n"
        content += reports.generate_tester_program_report() + "\n\n---\n\n"
        content += reports.generate_projects_status_report() + "\n\n---\n\n"
        content += reports.generate_financial_summary_report()
        title = 'Comprehensive Report'
    else:
        flash('Unknown report type', 'error')
        return redirect(url_for('reports_list'))

    flash(f'{title} generated!', 'success')
    return render_template('reports/view.html',
        content=content,
        title=title,
        report_type=report_type,
        generated_at=datetime.now().isoformat()
    )


@app.route('/reports/<report_type>')
def reports_view_type(report_type):
    """Generate and view a report by type."""
    if report_type == 'ideas':
        content = reports.generate_ideas_pipeline_report()
        title = 'Ideas Pipeline Report'
    elif report_type == 'testers':
        content = reports.generate_tester_program_report()
        title = 'Tester Program Report'
    elif report_type == 'projects':
        content = reports.generate_projects_status_report()
        title = 'Projects Status Report'
    elif report_type == 'finances':
        content = reports.generate_financial_summary_report()
        title = 'Financial Summary Report'
    else:
        flash('Unknown report type', 'error')
        return redirect(url_for('reports_list'))

    return render_template('reports/view.html',
        content=content,
        title=title,
        report_type=report_type,
        generated_at=datetime.now().isoformat()
    )


@app.route('/reports/view/<filename>')
def reports_view(filename):
    """View a saved report."""
    reports_dir = config.BASE_DIR / 'reports'
    report_path = reports_dir / filename

    if report_path.exists():
        content = report_path.read_text()
        return render_template('reports/view.html', content=content, report_type=filename)

    flash('Report not found', 'error')
    return redirect(url_for('reports_list'))


# =============================================================================
# MEETINGS & DECISIONS
# =============================================================================

@app.route('/meetings')
def meetings_list():
    """List past meetings."""
    meetings = list_meetings(limit=50)
    return render_template('meetings/list.html', meetings=meetings)


@app.route('/meetings/<path:filename>')
def meetings_view(filename):
    """View a meeting transcript."""
    meetings_dir = config.MEETINGS_DIR
    meeting_path = meetings_dir / filename

    if meeting_path.exists():
        content = meeting_path.read_text()
        return render_template('meetings/view.html', content=content, filename=filename)

    flash('Meeting not found', 'error')
    return redirect(url_for('meetings_list'))


@app.route('/meetings/detail/<meeting_id>')
def meetings_detail(meeting_id):
    """View meeting details by ID."""
    # For now, redirect to meetings list if not found
    # This would need a proper meeting store implementation
    flash('Meeting details view not yet implemented', 'info')
    return redirect(url_for('meetings_list'))


@app.route('/decisions')
def decisions_list():
    """List all decisions."""
    status_filter = request.args.get('status', '')
    topic_filter = request.args.get('topic', '')

    decisions = query_decisions(
        status=status_filter or None,
        topic=topic_filter or None,
        limit=100
    )

    # Calculate stats
    total_decisions = len(decisions)
    approved_decisions = len([d for d in decisions if d.get('finalized')])
    pending_decisions = total_decisions - approved_decisions

    return render_template('decisions/list.html',
        decisions=decisions,
        total_decisions=total_decisions,
        approved_decisions=approved_decisions,
        pending_decisions=pending_decisions,
        current_status=status_filter,
        current_topic=topic_filter
    )


# =============================================================================
# API ENDPOINTS (for AJAX)
# =============================================================================

@app.route('/api/stats')
def api_stats():
    """Get dashboard stats as JSON."""
    ideas_store = get_ideas_store()
    testers_store = get_testers_store()
    projects_store = get_projects_store()
    finances_store = get_finances_store()

    invoices = finances_store.get_invoices()
    outstanding = sum(i.get('amount', 0) for i in invoices
                     if i.get('status') in ['sent', 'overdue'])

    return jsonify({
        'ideas': len(ideas_store.get_all()),
        'ideas_pending': len(ideas_store.get_pending()),
        'testers': len(testers_store.get_all()),
        'testers_active': len(testers_store.get_available()),
        'projects': len(projects_store.get_all()),
        'projects_active': len(projects_store.get_active()),
        'outstanding': outstanding,
    })


# =============================================================================
# HTMX PARTIAL ENDPOINTS (for real-time updates)
# =============================================================================

@app.route('/htmx/agent/<agent_id>/stats')
def htmx_agent_stats(agent_id):
    """HTMX partial: Agent portal stats."""
    if agent_id not in AGENT_INFO:
        return '', 404

    store = get_agent_requests_store()
    requests = store.get_by_agent(agent_id)

    request_stats = {
        'total': len(requests),
        'pending': len([r for r in requests if r.get('status') in ['submitted', 'under_review']]),
        'approved': len([r for r in requests if r.get('status') == 'approved']),
        'implemented': len([r for r in requests if r.get('status') == 'implemented']),
    }

    return render_template('agents/partials/stats.html', request_stats=request_stats)


@app.route('/htmx/agent/<agent_id>/activity')
def htmx_agent_activity(agent_id):
    """HTMX partial: Agent recent activity."""
    if agent_id not in AGENT_INFO:
        return '', 404

    store = get_agent_requests_store()
    requests = store.get_by_agent(agent_id)
    recent_activity = sorted(requests, key=lambda x: x.get('created_at', ''), reverse=True)[:5]

    return render_template('agents/partials/activity.html', recent_activity=recent_activity)


@app.route('/htmx/agent/<agent_id>/requests')
def htmx_agent_requests(agent_id):
    """HTMX partial: Agent requests table."""
    if agent_id not in AGENT_INFO:
        return '', 404

    store = get_agent_requests_store()
    requests = store.get_by_agent(agent_id)

    return render_template('agents/partials/requests_table.html', requests=requests)


@app.route('/htmx/requests/pending/count')
def htmx_pending_count():
    """HTMX partial: Pending requests count badge."""
    store = get_agent_requests_store()
    count = len(store.get_pending())
    return f'<span class="badge bg-warning">{count}</span>'


@app.route('/htmx/dashboard/stats')
def htmx_dashboard_stats():
    """HTMX partial: Dashboard statistics."""
    ideas_store = get_ideas_store()
    testers_store = get_testers_store()
    projects_store = get_projects_store()
    finances_store = get_finances_store()

    invoices = finances_store.get_invoices()
    outstanding = sum(i.get('amount', 0) for i in invoices
                     if i.get('status') in ['sent', 'overdue'])

    return render_template('partials/dashboard_stats.html',
        ideas_count=len(ideas_store.get_all()),
        ideas_pending=len(ideas_store.get_pending()),
        testers_count=len(testers_store.get_all()),
        testers_active=len(testers_store.get_available()),
        projects_count=len(projects_store.get_all()),
        projects_active=len(projects_store.get_active()),
        outstanding=outstanding,
    )


# =============================================================================
# AGENT PORTALS
# =============================================================================

# Agent information for portal pages
AGENT_INFO = {
    'ceo': {
        'id': 'ceo',
        'name': 'Chief Executive Officer',
        'role': 'CEO',
        'team': 'executive',
        'description': 'Strategic leadership, vision setting, and overall company direction. Oversees all departments and makes final decisions on major initiatives.',
        'responsibilities': ['Company strategy', 'Team leadership', 'Client relationships', 'Business development'],
        'metrics': ['Revenue growth', 'Client retention', 'Team health'],
    },
    'cfo': {
        'id': 'cfo',
        'name': 'Chief Financial Officer',
        'role': 'CFO',
        'team': 'executive',
        'description': 'Financial planning, budgeting, and fiscal oversight. Manages company finances and ensures financial health.',
        'responsibilities': ['Budget management', 'Financial reporting', 'Cash flow', 'Pricing strategy'],
        'metrics': ['Profit margin', 'Cash flow', 'AR/AP health'],
    },
    'cito': {
        'id': 'cito',
        'name': 'Chief Information Technology Officer',
        'role': 'CITO',
        'team': 'executive',
        'description': 'Technical strategy and architecture decisions. Leads technology direction and oversees engineering teams.',
        'responsibilities': ['Tech strategy', 'Architecture decisions', 'Technical hiring', 'Innovation'],
        'metrics': ['Tech debt ratio', 'System uptime', 'Idea conversion'],
    },
    'sales': {
        'id': 'sales',
        'name': 'Sales Director',
        'role': 'Sales',
        'team': 'executive',
        'description': 'Business development and client acquisition. Manages sales pipeline and negotiates deals.',
        'responsibilities': ['Lead generation', 'Client pitches', 'Deal negotiation', 'Pipeline management'],
        'metrics': ['Pipeline value', 'Conversion rate', 'Deal velocity'],
    },
    'legal': {
        'id': 'legal',
        'name': 'Legal Counsel',
        'role': 'Legal',
        'team': 'executive',
        'description': 'Contract review, compliance, and risk management. Protects company interests and ensures legal compliance.',
        'responsibilities': ['Contract review', 'IP protection', 'Compliance', 'Risk assessment'],
        'metrics': ['Contract turnaround', 'Compliance status'],
    },
    'dev_lead': {
        'id': 'dev_lead',
        'name': 'Development Lead',
        'role': 'DevLead',
        'team': 'technical',
        'description': 'Engineering team leadership and code quality. Oversees development processes and technical implementation.',
        'responsibilities': ['Code reviews', 'Technical mentoring', 'Sprint planning', 'Architecture implementation'],
        'metrics': ['Code quality', 'Team velocity', 'Bug rate'],
    },
    'design_lead': {
        'id': 'design_lead',
        'name': 'Design Lead',
        'role': 'DesignLead',
        'team': 'technical',
        'description': 'User experience and visual design direction. Creates and maintains design systems and standards.',
        'responsibilities': ['UX design', 'Design systems', 'User research', 'Brand consistency'],
        'metrics': ['Design consistency', 'User satisfaction'],
    },
    'qa_lead': {
        'id': 'qa_lead',
        'name': 'Quality Assurance Lead',
        'role': 'QALead',
        'team': 'technical',
        'description': 'Quality standards and testing strategy. Ensures product quality through comprehensive testing.',
        'responsibilities': ['Test strategy', 'QA processes', 'Bug triage', 'Release certification'],
        'metrics': ['Bug escape rate', 'Test coverage', 'Release quality'],
    },
    'pm': {
        'id': 'pm',
        'name': 'Project Manager',
        'role': 'PM',
        'team': 'operations',
        'description': 'Project coordination and delivery management. Ensures projects are delivered on time and within scope.',
        'responsibilities': ['Project planning', 'Resource allocation', 'Stakeholder communication', 'Risk management'],
        'metrics': ['On-time delivery', 'Scope creep', 'Client satisfaction'],
    },
    'customer_success': {
        'id': 'customer_success',
        'name': 'Customer Success Manager',
        'role': 'CustomerSuccess',
        'team': 'operations',
        'description': 'Client relationship management post-sale. Ensures client satisfaction and identifies growth opportunities.',
        'responsibilities': ['Client onboarding', 'Success metrics', 'Relationship building', 'Upselling'],
        'metrics': ['NPS score', 'Retention rate', 'Expansion revenue'],
    },
    'marketing': {
        'id': 'marketing',
        'name': 'Marketing Director',
        'role': 'Marketing',
        'team': 'operations',
        'description': 'Brand strategy and marketing campaigns. Drives awareness and generates leads for the sales team.',
        'responsibilities': ['Brand strategy', 'Content marketing', 'ASO/SEO', 'Lead generation'],
        'metrics': ['App rankings', 'Traffic growth', 'Lead conversion'],
    },
    'support': {
        'id': 'support',
        'name': 'Support Lead',
        'role': 'Support',
        'team': 'operations',
        'description': 'Customer support and issue resolution. Manages support team and ensures timely issue resolution.',
        'responsibilities': ['Support operations', 'Issue triage', 'Knowledge base', 'Escalation management'],
        'metrics': ['Response time', 'Resolution rate', 'Satisfaction score'],
    },
}


@app.route('/agents')
def agents_list():
    """List all agent portals."""
    store = get_agent_requests_store()

    # Get all agents with their request counts
    all_requests = store.get_all()

    # Organize agents by team
    executive_team = []
    technical_team = []
    operations_team = []

    for agent_id, info in AGENT_INFO.items():
        agent_data = {
            **info,
            'request_count': len([r for r in all_requests if r.get('agent_id') == agent_id])
        }

        if info['team'] == 'executive':
            executive_team.append(agent_data)
        elif info['team'] == 'technical':
            technical_team.append(agent_data)
        else:
            operations_team.append(agent_data)

    # Calculate stats
    pending_count = len(store.get_pending())
    stats = {
        'total': len(all_requests),
        'submitted': len([r for r in all_requests if r.get('status') == 'submitted']),
        'under_review': len([r for r in all_requests if r.get('status') == 'under_review']),
        'approved': len([r for r in all_requests if r.get('status') == 'approved']),
        'implemented': len([r for r in all_requests if r.get('status') == 'implemented']),
        'rejected': len([r for r in all_requests if r.get('status') == 'rejected']),
    }

    return render_template('agents/list.html',
        executive_team=executive_team,
        technical_team=technical_team,
        operations_team=operations_team,
        pending_count=pending_count,
        stats=stats
    )


@app.route('/agents/<agent_id>')
def agent_portal(agent_id):
    """Individual agent portal."""
    if agent_id not in AGENT_INFO:
        flash('Agent not found', 'error')
        return redirect(url_for('agents_list'))

    agent = AGENT_INFO[agent_id]
    store = get_agent_requests_store()

    # Get agent's requests
    requests = store.get_by_agent(agent_id)

    # Calculate request stats for this agent
    request_stats = {
        'total': len(requests),
        'pending': len([r for r in requests if r.get('status') in ['submitted', 'under_review']]),
        'approved': len([r for r in requests if r.get('status') == 'approved']),
        'implemented': len([r for r in requests if r.get('status') == 'implemented']),
    }

    # Get recent activity (requests sorted by date)
    recent_activity = sorted(requests, key=lambda x: x.get('created_at', ''), reverse=True)[:5]

    return render_template('agents/portal.html',
        agent=agent,
        requests=requests,
        request_stats=request_stats,
        recent_activity=recent_activity,
        priorities=FeatureRequestPriority,
        statuses=FeatureRequestStatus
    )


@app.route('/agents/<agent_id>/request/new', methods=['GET', 'POST'])
def agent_request_new(agent_id):
    """Create a new feature request for an agent."""
    if agent_id not in AGENT_INFO:
        flash('Agent not found', 'error')
        return redirect(url_for('agents_list'))

    agent = AGENT_INFO[agent_id]

    if request.method == 'POST':
        store = get_agent_requests_store()

        feature_request = store.create_request(
            agent_id=agent_id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            request_type=request.form.get('request_type', 'feature'),
            priority=FeatureRequestPriority(request.form.get('priority', 'medium')),
            justification=request.form.get('justification', ''),
            affected_area=request.form.get('affected_area', ''),
        )

        flash(f'Feature request "{feature_request["title"]}" submitted!', 'success')
        return redirect(url_for('agent_portal', agent_id=agent_id))

    return render_template('agents/request_form.html',
        agent=agent,
        feature_request=None,
        priorities=FeatureRequestPriority
    )


@app.route('/agents/requests')
def agent_requests_all():
    """List all agent feature requests."""
    store = get_agent_requests_store()
    status_filter = request.args.get('status', '')
    agent_filter = request.args.get('agent', '')

    if status_filter:
        requests_list = store.get_by_status(FeatureRequestStatus(status_filter))
    elif agent_filter:
        requests_list = store.get_by_agent(agent_filter)
    else:
        requests_list = store.get_all()

    # Sort by created_at descending
    requests_list = sorted(requests_list, key=lambda x: x.get('created_at', ''), reverse=True)

    # Enrich with agent info
    for req in requests_list:
        req['_agent'] = AGENT_INFO.get(req.get('agent_id', ''), {})

    return render_template('agents/requests_list.html',
        requests=requests_list,
        agents=AGENT_INFO,
        statuses=FeatureRequestStatus,
        priorities=FeatureRequestPriority,
        current_status=status_filter,
        current_agent=agent_filter
    )


@app.route('/agents/requests/pending')
def agent_requests_pending():
    """List pending feature requests for review."""
    store = get_agent_requests_store()
    pending = store.get_pending()

    # Sort by priority (critical first) then by date
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    pending = sorted(pending, key=lambda x: (
        priority_order.get(x.get('priority', 'medium'), 2),
        x.get('created_at', '')
    ))

    # Enrich with agent info
    for req in pending:
        req['_agent'] = AGENT_INFO.get(req.get('agent_id', ''), {})

    return render_template('agents/requests_pending.html',
        requests=pending,
        agents=AGENT_INFO,
        statuses=FeatureRequestStatus
    )


@app.route('/agents/requests/<request_id>')
def agent_request_detail(request_id):
    """View feature request details."""
    store = get_agent_requests_store()
    feature_request = store.get_by_id(request_id)

    if not feature_request:
        flash('Request not found', 'error')
        return redirect(url_for('agent_requests_all'))

    agent = AGENT_INFO.get(feature_request.get('agent_id', ''), {})

    return render_template('agents/request_detail.html',
        request=feature_request,
        agent=agent,
        statuses=FeatureRequestStatus,
        priorities=FeatureRequestPriority
    )


@app.route('/agents/requests/<request_id>/status', methods=['POST'])
def agent_request_update_status(request_id):
    """Update feature request status."""
    store = get_agent_requests_store()
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    reviewer = request.form.get('reviewer', 'Architect')

    result = store.update_status(request_id, FeatureRequestStatus(new_status), reviewer, notes)

    if result:
        flash(f'Status updated to {new_status}', 'success')
    else:
        flash('Failed to update status', 'error')

    return redirect(url_for('agent_request_detail', request_id=request_id))


@app.route('/agents/requests/<request_id>/approve', methods=['POST'])
def agent_request_approve(request_id):
    """Approve a feature request."""
    store = get_agent_requests_store()
    notes = request.form.get('notes', '')
    reviewer = request.form.get('reviewer', 'Architect')

    result = store.approve(request_id, reviewer, notes)

    if result:
        flash('Request approved!', 'success')
    else:
        flash('Failed to approve request', 'error')

    return redirect(url_for('agent_request_detail', request_id=request_id))


@app.route('/agents/requests/<request_id>/reject', methods=['POST'])
def agent_request_reject(request_id):
    """Reject a feature request."""
    store = get_agent_requests_store()
    reason = request.form.get('reason', 'No reason provided')
    reviewer = request.form.get('reviewer', 'Architect')

    result = store.reject(request_id, reviewer, reason)

    if result:
        flash('Request rejected', 'warning')
    else:
        flash('Failed to reject request', 'error')

    return redirect(url_for('agent_request_detail', request_id=request_id))


@app.route('/agents/requests/<request_id>/vote', methods=['POST'])
def agent_request_vote(request_id):
    """Vote on a feature request (by other agents)."""
    store = get_agent_requests_store()
    agent_id = request.form.get('agent_id')
    vote_type = request.form.get('vote_type', 'support')

    result = store.vote(request_id, agent_id, vote_type)

    if result:
        flash(f'Vote recorded ({vote_type})', 'success')
    else:
        flash('Failed to record vote', 'error')

    return redirect(url_for('agent_request_detail', request_id=request_id))


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
