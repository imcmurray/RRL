// Rinse Repeat Labs Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Status filter handling
    var statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            var url = new URL(window.location.href);
            if (this.value) {
                url.searchParams.set('status', this.value);
            } else {
                url.searchParams.delete('status');
            }
            window.location.href = url.toString();
        });
    }

    // Search functionality
    var searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            var searchTerm = this.value.toLowerCase();
            var tableRows = document.querySelectorAll('tbody tr');

            tableRows.forEach(function(row) {
                var text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Dynamic field arrays (for platforms, skills, etc.)
    setupDynamicFields();

    // Auto-refresh dashboard stats
    if (document.getElementById('dashboardStats')) {
        setInterval(refreshDashboardStats, 60000); // Refresh every minute
    }
});

// Debounce function for search
function debounce(func, wait) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}

// Setup dynamic field handling
function setupDynamicFields() {
    var addFieldButtons = document.querySelectorAll('[data-add-field]');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var targetId = this.getAttribute('data-add-field');
            var container = document.getElementById(targetId);
            var template = container.querySelector('.field-template');

            if (template) {
                var clone = template.cloneNode(true);
                clone.classList.remove('field-template', 'd-none');
                clone.querySelector('input').value = '';
                container.insertBefore(clone, template);
            }
        });
    });

    // Remove field handling
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-remove-field]')) {
            e.target.closest('.field-group').remove();
        }
    });
}

// Refresh dashboard stats via API
function refreshDashboardStats() {
    fetch('/api/stats')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            // Update stat values
            updateStatValue('ideas-count', data.ideas.total);
            updateStatValue('testers-count', data.testers.active);
            updateStatValue('projects-count', data.projects.active);
            updateStatValue('revenue-total', formatCurrency(data.finances.total_revenue));
        })
        .catch(function(error) {
            console.error('Error refreshing stats:', error);
        });
}

function updateStatValue(elementId, value) {
    var element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy', 'error');
    });
}

// Toast notification helper
function showToast(message, type) {
    var toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    var toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center text-white bg-' + (type === 'error' ? 'danger' : 'success');
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML =
        '<div class="d-flex">' +
            '<div class="toast-body">' + message + '</div>' +
            '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
        '</div>';

    toastContainer.appendChild(toastEl);
    var toast = new bootstrap.Toast(toastEl);
    toast.show();

    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

// Export report functionality
function exportReport(reportId, format) {
    window.location.href = '/reports/' + reportId + '/export?format=' + format;
}

// Run agent meeting
function runMeeting(meetingType, topic) {
    if (!topic) {
        topic = prompt('Enter meeting topic:');
        if (!topic) return;
    }

    showToast('Starting ' + meetingType + ' meeting...', 'info');

    fetch('/api/meetings/run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: meetingType,
            topic: topic
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            showToast('Meeting completed!', 'success');
            window.location.href = '/meetings/' + data.meeting_id;
        } else {
            showToast('Meeting failed: ' + data.error, 'error');
        }
    })
    .catch(function(error) {
        showToast('Error running meeting', 'error');
        console.error('Error:', error);
    });
}
