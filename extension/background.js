const API_URL = "http://localhost:8000/scan";

// Cache to prevent repetitive scanning of the same URL in short time
const scanCache = new Map();

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    const { url, tabId, frameId } = details;

    // Only scan main frame
    if (frameId !== 0) return;

    // Skip internal pages
    if (url.startsWith("chrome://") || url.startsWith("chrome-extension://") || url.startsWith("about:")) return;

    // Check allowlist in storage (User Override)
    const { allowedUrls } = await chrome.storage.local.get("allowedUrls");
    if (allowedUrls && allowedUrls[url]) {
        console.log("Skipping allowed URL:", url);
        return;
    }

    // Check Memory Cache
    if (scanCache.has(url)) {
        const cachedResult = scanCache.get(url);
        if (!cachedResult.safe) {
            redirectToInterstitial(tabId, url, cachedResult.reason);
        }
        return;
    }

    // Scan URL
    try {
        console.log("Scanning:", url);
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) throw new Error("Backend error");

        const result = await response.json();
        console.log("Scan Result:", result);

        // Cache result (valid for 5 mins)
        scanCache.set(url, result);
        setTimeout(() => scanCache.delete(url), 300000);

        if (!result.safe) {
            redirectToInterstitial(tabId, url, result.reason);
        } else {
            // Update badge for safe site
            chrome.action.setBadgeText({ tabId, text: "SAFE" });
            chrome.action.setBadgeBackgroundColor({ tabId, color: "#4CAF50" });
        }

    } catch (error) {
        console.error("Scan failed:", error);
        // Fail open (allow access) or warn? 
        // For prototype, we log.
        chrome.action.setBadgeText({ tabId, text: "ERR" });
        chrome.action.setBadgeBackgroundColor({ tabId, color: "#9E9E9E" });
    }
});

function redirectToInterstitial(tabId, targetUrl, reason) {
    const interstitialUrl = chrome.runtime.getURL("interstitial.html") +
        `?target=${encodeURIComponent(targetUrl)}&reason=${encodeURIComponent(reason)}`;
    chrome.tabs.update(tabId, { url: interstitialUrl });
}

// VPN Proxy Logic
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "setProxy") {
        if (!chrome.proxy) {
            console.error("chrome.proxy API not available. Check permissions.");
            sendResponse({ success: false, error: "permissions_missing" });
            return;
        }

        const config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: request.protocol || "http",
                    host: request.host,
                    port: parseInt(request.port)
                },
                bypassList: ["localhost", "127.0.0.1", "::1"]
            }
        };

        console.log("Attempting to set proxy:", config);

        chrome.proxy.settings.set({ value: config, scope: "regular" }, () => {
            if (chrome.runtime.lastError) {
                console.error("Error setting proxy:", chrome.runtime.lastError);
                sendResponse({ success: false, error: chrome.runtime.lastError.message });
                return;
            }

            // Verify
            chrome.proxy.settings.get({ 'incognito': false }, (details) => {
                console.log("Current Proxy Settings:", details);
                sendResponse({ success: true, details: details });
            });
        });
        return true; // Async response
    } else if (request.type === "clearProxy") {
        if (!chrome.proxy) {
            sendResponse({ success: false, error: "permissions_missing" });
            return;
        }
        chrome.proxy.settings.clear({ scope: "regular" }, () => {
            console.log("Proxy cleared");
            sendResponse({ success: true });
        });
        return true;
    }
});
