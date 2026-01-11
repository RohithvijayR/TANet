// --- Original Popup Logic ---
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
        const url = new URL(tabs[0].url);
        document.getElementById('currentUrl').textContent = "Domain: " + url.hostname;
    }
});

// --- VPN Logic ---
const vpnToggle = document.getElementById('vpnToggle');
const vpnStatus = document.getElementById('vpnStatus');
const configBtn = document.getElementById('configBtn');
const configForm = document.getElementById('configForm');
const saveConfig = document.getElementById('saveConfig');

const proxyHost = document.getElementById('proxyHost');
const proxyPort = document.getElementById('proxyPort');
const proxyProtocol = document.getElementById('proxyProtocol');

// Load Initial State
chrome.storage.local.get(['vpnEnabled', 'proxyConfig'], (data) => {
    vpnToggle.checked = !!data.vpnEnabled;
    updateStatusUI(data.vpnEnabled);

    if (data.proxyConfig) {
        proxyHost.value = data.proxyConfig.host || "13.53.35.65";
        proxyPort.value = data.proxyConfig.port || "8888";
        proxyProtocol.value = data.proxyConfig.protocol || "http";
    }
});

// Configure Button
configBtn.onclick = () => {
    configForm.style.display = configForm.style.display === 'none' ? 'block' : 'none';
};

// Save Configuration
saveConfig.onclick = () => {
    const config = {
        host: proxyHost.value,
        port: proxyPort.value,
        protocol: proxyProtocol.value
    };

    chrome.storage.local.set({ proxyConfig: config }, () => {
        configForm.style.display = 'none';
        alert("Settings Saved. Toggle VPN to apply.");
        // If VPN is on, re-apply
        if (vpnToggle.checked) {
            applyProxy(config);
        }
    });
};

// Toggle Switch
vpnToggle.onchange = () => {
    const enabled = vpnToggle.checked;
    chrome.storage.local.set({ vpnEnabled: enabled });
    updateStatusUI(enabled);

    if (enabled) {
        chrome.storage.local.get("proxyConfig", (data) => {
            const config = data.proxyConfig || {
                host: proxyHost.value,
                port: proxyPort.value,
                protocol: proxyProtocol.value
            };
            applyProxy(config);
        });
    } else {
        chrome.runtime.sendMessage({ type: "clearProxy" });
    }
};

function updateStatusUI(enabled) {
    if (enabled) {
        vpnStatus.textContent = "VPN Connected";
        vpnStatus.style.color = "#4CAF50";
        vpnStatus.style.fontWeight = "bold";
    } else {
        vpnStatus.textContent = "Disconnected";
        vpnStatus.style.color = "#e00000ff";
        vpnStatus.style.fontWeight = "normal";
    }
}

const debugBtn = document.getElementById('debugBtn');
const debugOutput = document.getElementById('debugOutput');

debugBtn.onclick = () => {
    debugOutput.style.display = debugOutput.style.display === 'none' ? 'block' : 'none';
    checkProxyStatus();
};

function checkProxyStatus() {
    if (!chrome.proxy) {
        debugOutput.textContent = "Error: chrome.proxy API missing (Permissions?)";
        return;
    }
    chrome.proxy.settings.get({ 'incognito': false }, (config) => {
        debugOutput.textContent = JSON.stringify(config, null, 2);

        // Highlight critical issues
        if (config.levelOfControl === 'controlled_by_other_extension') {
            vpnStatus.textContent = "Error: Another extension is controlling proxy!";
            vpnStatus.style.color = "red";
        } else if (config.levelOfControl === 'not_controllable') {
            vpnStatus.textContent = "Error: Proxy settings check prohibited by policy.";
            vpnStatus.style.color = "red";
        }
    });
}

function applyProxy(config) {
    chrome.runtime.sendMessage({
        type: "setProxy",
        host: config.host,
        port: config.port,
        protocol: config.protocol
    }, (response) => {
        if (response && response.success) {
            checkProxyStatus(); // Refresh debug info
        } else {
            console.error("Proxy error:", response);
            debugOutput.textContent = "Set Error: " + JSON.stringify(response);
        }
    });
}
