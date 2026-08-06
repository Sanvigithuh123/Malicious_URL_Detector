from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re

# ── 1. Start Flask ────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # allows chrome extension to talk to this server

# ── 2. Load trained model ─────────────────────────────────────────
print("Loading model...")
model = joblib.load("model.pkl")
print("Model loaded successfully")

# ── 3. Feature extraction (exact same as train.py) ────────────────
def extract_features(url):
    url = str(url)

    try:
        domain = url.split("//")[1].split("/")[0]
    except:
        domain = url

    try:
        path = url.split("//")[1].split("/", 1)[1] if "/" in url.split("//")[1] else ""
    except:
        path = ""

    suspicious_keywords = ["login", "verify", "secure", "account",
                           "update", "banking", "confirm", "signin",
                           "paypal", "ebay", "apple", "microsoft"]
    has_suspicious = 1 if any(k in url.lower() for k in suspicious_keywords) else 0

    is_ip = 1 if re.match(r"^\d+\.\d+\.\d+\.\d+", domain) else 0

    suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".ru", ".xyz", ".top"]
    has_suspicious_tld = 1 if any(domain.endswith(t) for t in suspicious_tlds) else 0

    return [
        len(url),
        1 if url.startswith("https") else 0,
        url.count("."),
        url.count("-"),
        url.count("@"),
        url.count("?"),
        url.count("="),
        url.count("/"),
        len(re.findall(r"[@#$%&\-_=?]", url)),
        1 if any(c.isdigit() for c in domain) else 0,  # digits in DOMAIN, not full url
        len(domain),
        len(path),
        url.count("//"),
        has_suspicious,
        is_ip,
        has_suspicious_tld,
    ]

# ── 4. Predict route ──────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():

    # get URL sent by extension
    data = request.get_json()

    # check if URL was actually sent
    if not data or "url" not in data:
        return jsonify({"error": "no url provided"}), 400

    url = data["url"]

    # convert URL to numbers
    features = extract_features(url)

    # run through model
    prediction = model.predict([features])[0]

    # get probability score
    score = model.predict_proba([features])[0][1] * 100

    # decide label
    label = "malicious" if prediction == 1 else "safe"

    # decide color for extension popup
    if score >= 70:
        color = "red"
    elif score >= 40:
        color = "orange"
    else:
        color = "green"

    print(f"URL: {url}")
    print(f"Label: {label}")
    print(f"Score: {round(score, 2)}%")
    print("─" * 40)

    # send result back to extension
    return jsonify({
        "url": url,
        "label": label,
        "score": round(score, 2),
        "color": color
    })

# ── 5. Home route (just to check server is running) ───────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "server is running"})

# ── 6. Run the server ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
