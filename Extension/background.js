chrome.webNavigation.onCompleted.addListener(async (details) => {

    if (details.frameId !== 0) return

    const url = details.url

    if (url.startsWith("chrome://")) return
    if (url.startsWith("chrome-extension://")) return
    if (url.startsWith("about://")) return

    console.log("New page detected:", url)

    try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
        })

        const result = await response.json()
        console.log("Result:", result)

        // ── wait 2 seconds for page and content.js to fully load ──
        setTimeout(async () => {
            try {
                await chrome.tabs.sendMessage(details.tabId, {
                    action: "showPopup",
                    result: result
                })
                console.log("Message sent successfully")
            } catch (err) {
                console.log("Message failed, injecting directly:", err)

                // ── if message fails inject script directly ────────
                await chrome.scripting.executeScript({
                    target: { tabId: details.tabId },
                    func: (result) => {
                        const existing = document.getElementById("url-safety-popup")
                        if (existing) existing.remove()

                        let bgColor, borderColor, textColor, icon
                        if (result.color === "red") {
                            icon = "🔴"; bgColor = "#fff5f5"; borderColor = "#fc8181"; textColor = "#c53030"
                        } else if (result.color === "orange") {
                            icon = "🟡"; bgColor = "#fffaf0"; borderColor = "#f6ad55"; textColor = "#c05621"
                        } else {
                            icon = "🟢"; bgColor = "#f0fff4"; borderColor = "#68d391"; textColor = "#276749"
                        }

                        const popup = document.createElement("div")
                        popup.id = "url-safety-popup"
                        popup.style.cssText = `position:fixed;top:20px;right:20px;width:300px;background:${bgColor};border:2px solid ${borderColor};border-radius:12px;padding:16px;box-shadow:0 4px 20px rgba(0,0,0,0.15);z-index:999999;font-family:Arial`
                        popup.innerHTML = `
                            <div style="display:flex;justify-content:space-between;align-items:center">
                                <span style="font-size:18px;font-weight:bold;color:${textColor}">${icon} ${result.label.toUpperCase()}</span>
                                <button onclick="this.parentElement.parentElement.remove()" style="background:none;border:none;font-size:18px;cursor:pointer;color:#999">✕</button>
                            </div>
                            <p style="margin:10px 0 0;font-size:13px;color:#555">Risk Score: <strong>${result.score}%</strong></p>
                            <p style="margin:6px 0 0;font-size:11px;color:#777;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${result.url}</p>
                        `
                        document.body.appendChild(popup)
                        setTimeout(() => popup.remove(), 10000)
                    },
                    args: [result]
                })
            }
        }, 2000)

    } catch (error) {
        console.log("Flask server error:", error)
    }
})
