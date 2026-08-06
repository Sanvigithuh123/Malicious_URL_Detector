// ── immediately tell background we are ready ──────────────────────
console.log("content.js loaded")

// ── listen for messages ───────────────────────────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("message received in content.js", message)
    if (message.action === "showPopup") {
        showPopup(message.result)
    }
    sendResponse({ received: true })
    return true
})

function showPopup(result) {
    console.log("showPopup called", result)

    const existing = document.getElementById("url-safety-popup")
    if (existing) existing.remove()

    let icon, bgColor, borderColor, textColor

    if (result.color === "red") {
        icon = "🔴"
        bgColor = "#fff5f5"
        borderColor = "#fc8181"
        textColor = "#c53030"
    } else if (result.color === "orange") {
        icon = "🟡"
        bgColor = "#fffaf0"
        borderColor = "#f6ad55"
        textColor = "#c05621"
    } else {
        icon = "🟢"
        bgColor = "#f0fff4"
        borderColor = "#68d391"
        textColor = "#276749"
    }

    const popup = document.createElement("div")
    popup.id = "url-safety-popup"
    popup.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        width: 300px;
        background: ${bgColor};
        border: 2px solid ${borderColor};
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        z-index: 999999;
        font-family: Arial, sans-serif;
    `

    popup.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:18px; font-weight:bold; color:${textColor};">
                ${icon} ${result.label.toUpperCase()}
            </span>
            <button id="close-btn" style="
                background:none;
                border:none;
                font-size:18px;
                cursor:pointer;
                color:#999;
            ">✕</button>
        </div>

        <div style="margin-top:10px;">
            <div style="
                background:#e2e8f0;
                border-radius:999px;
                height:10px;
                width:100%;
            ">
                <div style="
                    width:${result.score}%;
                    background:${borderColor};
                    height:10px;
                    border-radius:999px;
                "></div>
            </div>
            <p style="margin:6px 0 0; font-size:13px; color:#555;">
                Risk Score: <strong>${result.score}%</strong>
            </p>
        </div>

        <div style="margin-top:10px; font-size:12px; color:#777;
                    white-space:nowrap; overflow:hidden;
                    text-overflow:ellipsis;">
            ${result.url}
        </div>

        <button id="details-btn" style="
            margin-top:12px;
            width:100%;
            padding:8px;
            background:none;
            border:1px solid ${borderColor};
            border-radius:8px;
            color:${textColor};
            cursor:pointer;
            font-size:13px;
        ">Details ▼</button>

        <div id="details-panel" style="display:none; margin-top:10px;
             font-size:12px; color:#555; border-top:1px solid ${borderColor};
             padding-top:10px;">
            <p>URL Length: ${result.url.length} chars</p>
            <p>HTTPS: ${result.url.startsWith("https") ? "✓ Yes" : "✗ No"}</p>
            <p>Dots: ${result.url.split(".").length - 1}</p>
            <p>Special Characters: ${(result.url.match(/[@#$%&\-_=?]/g) || []).length}</p>
        </div>
    `

    document.body.appendChild(popup)

    document.getElementById("close-btn").addEventListener("click", () => {
        popup.remove()
    })

    document.getElementById("details-btn").addEventListener("click", () => {
        const panel = document.getElementById("details-panel")
        if (panel.style.display === "none") {
            panel.style.display = "block"
            document.getElementById("details-btn").textContent = "Details ▲"
        } else {
            panel.style.display = "none"
            document.getElementById("details-btn").textContent = "Details ▼"
        }
    })

    setTimeout(() => {
        if (document.getElementById("url-safety-popup")) {
            popup.remove()
        }
    }, 10000)
}
