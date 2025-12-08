// JavaScript for QR code admin functionality

function regenerateQR(animalId) {
    if (!confirm('Are you sure you want to regenerate the QR code for this animal?')) {
        return;
    }
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Make API call to regenerate QR code
    fetch(`/api/v1/animals/${animalId}/regenerate_qr/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert('QR code regenerated successfully!');
            // Reload the page to show the new QR code
            window.location.reload();
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to regenerate QR code. Please try again.');
    });
}

// Add copy QR data functionality
function copyQRData(data) {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(function() {
        alert('QR data copied to clipboard!');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add styling for QR code previews
    const style = document.createElement('style');
    style.textContent = `
        .qr-preview-container {
            margin: 10px 0;
            padding: 15px;
            border: 1px solid #ddd;
            background: #fafafa;
            border-radius: 4px;
        }
        .qr-data-container {
            max-height: 200px;
            overflow-y: auto;
            margin: 10px 0;
        }
        .button.regenerate-qr {
            background-color: #007cba;
            color: white;
            margin-left: 10px;
        }
        .button.regenerate-qr:hover {
            background-color: #005a87;
        }
    `;
    document.head.appendChild(style);
});