/**
 * KoboToolbox Sync JavaScript
 * Handles manual sync operations and real-time updates
 */

function manualSyncToKobo(formTemplateId) {
    if (!confirm('Sync this form to KoboToolbox? This will update the form structure and reference data.')) {
        return;
    }

    // Show loading indicator
    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    // Use textContent for security, then add spinner via DOM manipulation
    btn.textContent = '';
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm me-2';
    btn.appendChild(spinner);
    btn.appendChild(document.createTextNode('Syncing...'));

    fetch(`/forms/kobo/sync/${formTemplateId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', '✓ Form synced successfully to KoboToolbox!');

            // Show Kobo form URL if available
            if (data.form_url) {
                // Validate URL before displaying (basic security check)
                try {
                    const url = new URL(data.form_url);
                    if (url.hostname.includes('kobotoolbox.org')) {
                        showAlert('info', `Form available at: ${data.form_url}`, false);
                    }
                } catch (e) {
                    // Invalid URL, don't show
                }
            }

            // Reload page after short delay
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert('error', `✗ Sync failed: ${data.message}`);
            btn.disabled = false;
            btn.textContent = originalText;
        }
    })
    .catch(error => {
        showAlert('error', `Error: ${error.message}`);
        btn.disabled = false;
        btn.textContent = originalText;
    });
}

function showAlert(type, message, isHtml = false) {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';

    // Security: Use textContent for plain text, only allow HTML for trusted content
    if (isHtml && type === 'info') {
        // Only allow HTML for info messages with trusted content (URLs from server)
        alertDiv.innerHTML = message;
    } else {
        // Use textContent to prevent XSS for user-controlled content
        alertDiv.textContent = message;
    }

    // Add close button via DOM manipulation
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'btn-close';
    closeBtn.setAttribute('data-bs-dismiss', 'alert');
    alertDiv.appendChild(closeBtn);

    document.body.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Auto-refresh sync status every 30 seconds if syncing
function autoRefreshSyncStatus() {
    const syncStatusElement = document.querySelector('[data-sync-status]');
    if (syncStatusElement) {
        const status = syncStatusElement.dataset.syncStatus;
        if (status === 'sync_pending') {
            setTimeout(() => location.reload(), 30000);
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    autoRefreshSyncStatus();
});
