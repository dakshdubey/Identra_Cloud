let currentMode = 'verify'; // 'verify' or 'register'

function switchMode(mode) {
    currentMode = mode;
    const inputGroup = document.getElementById('enroll-input-group');
    const btnAction = document.getElementById('btn-action');
    const btnVerify = document.getElementById('btn-verify');
    const btnRegister = document.getElementById('btn-register');
    const statusText = document.getElementById('status-text');
    const statusSubtext = document.getElementById('status-subtext');

    if (mode === 'register') {
        // UI for Registration
        inputGroup.style.display = 'block';
        btnAction.textContent = 'Capture Bio-ID';
        btnAction.style.display = 'flex';

        // Toggle Active Styles
        btnRegister.classList.remove('btn-glass');
        btnRegister.classList.add('btn-primary');
        btnVerify.classList.remove('btn-primary');
        btnVerify.classList.add('btn-glass');

        statusText.textContent = "New Agent Enrollment";
        statusSubtext.textContent = "Enter ID and scan face";

    } else {
        // UI for Verification
        inputGroup.style.display = 'none';
        btnAction.textContent = 'Authenticate';
        btnAction.style.display = 'flex'; // Actually we can just keep the split buttons, but for a constrained UI let's use a main action button pattern if we want. 
        // Let's revert to the dual button design for simplicity, or use the 'Action' button to confirm.
        // Let's use the 'Action' button as the primary trigger.

        // Toggle Active Styles
        btnVerify.classList.remove('btn-glass');
        btnVerify.classList.add('btn-primary');
        btnRegister.classList.remove('btn-primary');
        btnRegister.classList.add('btn-glass');

        statusText.textContent = "Identity Verification";
        statusSubtext.textContent = "Ready to scan";
    }
}

async function executeAction() {
    const statusIcon = document.getElementById('status-icon');
    const statusText = document.getElementById('status-text');
    const pulseRing = document.getElementById('pulse-ring');
    const userIdInput = document.getElementById('user-id-input');

    // Reset UI
    statusIcon.style.color = 'var(--text-muted)';
    pulseRing.style.opacity = '1';
    pulseRing.style.animation = 'pulse-ring 1.5s infinite';
    statusText.textContent = "Initializing Sensor...";

    try {
        let endpoint = '';
        let body = {};

        if (currentMode === 'register') {
            const userId = userIdInput.value;
            if (!userId) {
                alert("Please enter a User ID");
                pulseRing.style.opacity = '0';
                return;
            }
            endpoint = '/api/register-auto';
            body = { user_id: userId };
        } else {
            endpoint = '/api/verify-auto';
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        // Stop Animation
        pulseRing.style.animation = 'none';
        pulseRing.style.opacity = '0';

        if (data.status === 'success') {
            statusIcon.className = "fa-solid fa-shield-check";
            statusIcon.style.color = "var(--accent-success)";
            statusText.textContent = "Access Granted";

            // If verify, redirect to dashboard
            if (currentMode === 'verify') {
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1000);
            } else {
                statusText.textContent = "Enrollment Complete";
            }

        } else {
            statusIcon.className = "fa-solid fa-circle-xmark";
            statusIcon.style.color = "var(--accent-error)";
            statusText.textContent = "Access Denied";
            alert(data.message || "Operation failed");
        }

    } catch (error) {
        console.error(error);
        statusText.textContent = "System Error";
        pulseRing.style.opacity = '0';
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    switchMode('verify'); // Default state
});
