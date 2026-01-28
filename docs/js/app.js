/**
 * Rinse Repeat Labs Demo - Application JavaScript
 */

// Theme toggle functionality
(function() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeLabel = document.getElementById('theme-label');

    // Get stored theme or default to light
    const storedTheme = localStorage.getItem('rrl-demo-theme') || 'light';
    html.setAttribute('data-bs-theme', storedTheme);
    updateThemeUI(storedTheme);

    // Theme toggle click handler
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const currentTheme = html.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            html.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('rrl-demo-theme', newTheme);
            updateThemeUI(newTheme);
        });
    }

    function updateThemeUI(theme) {
        if (themeIcon && themeLabel) {
            if (theme === 'dark') {
                themeIcon.className = 'bi bi-moon-fill me-2';
                themeLabel.textContent = 'Dark Mode';
            } else {
                themeIcon.className = 'bi bi-sun-fill me-2';
                themeLabel.textContent = 'Light Mode';
            }
        }
    }
})();

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

// Simulated typing effect for AI responses
function typeMessage(element, text, speed = 20) {
    return new Promise((resolve) => {
        let i = 0;
        element.textContent = '';

        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }

        type();
    });
}

// Show typing indicator
function showTypingIndicator(container) {
    const indicator = document.createElement('div');
    indicator.className = 'chat-message agent';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
    return indicator;
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Add chat message to container
function addChatMessage(container, message, isUser = false, agentName = null, agentId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'agent'}`;

    if (!isUser && agentName) {
        const agentColor = DemoData.agents[agentId]?.color || '#6c757d';
        messageDiv.innerHTML = `
            <div class="agent-name" style="color: ${agentColor}">${agentName}</div>
            <div class="message-text">${message}</div>
        `;
    } else {
        messageDiv.innerHTML = `<div class="message-text">${message}</div>`;
    }

    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;

    return messageDiv;
}

// Simulate AI response with delay
async function simulateAIResponse(container, agentId, agentName) {
    // Show typing indicator
    showTypingIndicator(container);

    // Simulate thinking time (1-3 seconds)
    const thinkTime = 1000 + Math.random() * 2000;
    await new Promise(resolve => setTimeout(resolve, thinkTime));

    // Remove typing indicator
    removeTypingIndicator();

    // Get mock response
    const response = getMockResponse(agentId);

    // Add message with typing effect
    const messageDiv = addChatMessage(container, '', false, agentName, agentId);
    const textElement = messageDiv.querySelector('.message-text');
    await typeMessage(textElement, response, 15);

    return response;
}

// Toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    toastContainer.appendChild(toast);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 150);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1050; max-width: 350px;';
    document.body.appendChild(container);
    return container;
}

// Demo mode notification on first visit
(function() {
    if (!localStorage.getItem('rrl-demo-visited')) {
        localStorage.setItem('rrl-demo-visited', 'true');

        // Show welcome modal or toast on first visit
        setTimeout(() => {
            showToast(
                '<strong>Welcome to the Demo!</strong><br>This is a static demo with sample data. Explore the dashboard to see what Rinse Repeat Labs can do.',
                'info'
            );
        }, 1000);
    }
})();

// Handle form submissions in demo mode
document.addEventListener('submit', function(e) {
    const form = e.target;

    // Check if this is a demo form
    if (form.classList.contains('demo-form')) {
        e.preventDefault();
        showToast('This action is simulated in demo mode. In the full application, your changes would be saved.', 'warning');
    }
});

// Export functions for use in other scripts
window.RRLDemo = {
    formatCurrency,
    formatDate,
    typeMessage,
    showTypingIndicator,
    removeTypingIndicator,
    addChatMessage,
    simulateAIResponse,
    showToast
};
