const params = new URLSearchParams(window.location.search);
const target = params.get('target');
const reason = params.get('reason');
const API_URL = "http://localhost:8000";

document.getElementById('targetUrl').textContent = target;
document.getElementById('reason').textContent = "Reason: " + (reason || "Suspicious Patterns");

document.getElementById('goBack').onclick = () => {
    // If there is history, go back. Otherwise (new tab), close it.
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.close(); // Close tab if opened directly or no history
    }
};

document.getElementById('proceed').onclick = () => {
    // Add to allowlist for this session/permanent
    chrome.storage.local.get("allowedUrls", (data) => {
        const allowed = data.allowedUrls || {};
        allowed[target] = true;
        chrome.storage.local.set({ allowedUrls: allowed }, () => {
            window.location.href = target;
        });
    });
};

document.getElementById('reportSafe').onclick = async (e) => {
    e.preventDefault();
    const btn = document.getElementById('reportSafe');
    const originalText = btn.textContent;
    btn.textContent = "Reporting...";

    try {
        const response = await fetch(`${API_URL}/report`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: target, vote: "safe" })
        });

        if (response.ok) {
            btn.textContent = "Reported! (Processing...)";
            btn.style.textDecoration = "none";
            btn.style.cursor = "default";
            btn.onclick = null; // Disable further clicks
        } else {
            console.error(await response.text());
            btn.textContent = "Error reporting";
            setTimeout(() => btn.textContent = originalText, 2000);
        }
    } catch (err) {
        console.error(err);
        btn.textContent = "Network error";
        setTimeout(() => btn.textContent = originalText, 2000);
    }
};
