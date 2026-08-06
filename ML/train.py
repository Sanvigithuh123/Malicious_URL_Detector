import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils import resample
import joblib
import re

# ── 1. Load dataset ───────────────────────────────────────────────
df = pd.read_csv("malicious_phish.csv")
print(f"Total URLs loaded: {len(df)}")

# ── 2. Add real safe URLs ─────────────────────────────────────────
extra_safe = pd.DataFrame({
    "url": [
        "https://google.com",
        "https://www.google.com",
        "https://github.com",
        "https://www.github.com",
        "https://wikipedia.org",
        "https://www.wikipedia.org",
        "https://youtube.com",
        "https://www.youtube.com",
        "https://stackoverflow.com",
        "https://www.stackoverflow.com",
        "https://reddit.com",
        "https://www.reddit.com",
        "https://linkedin.com",
        "https://www.linkedin.com",
        "https://amazon.com",
        "https://www.amazon.com",
        "https://netflix.com",
        "https://www.netflix.com",
        "https://microsoft.com",
        "https://www.microsoft.com",
        "https://apple.com",
        "https://www.apple.com",
        "https://twitter.com",
        "https://www.twitter.com",
        "https://instagram.com",
        "https://www.instagram.com",
        "https://facebook.com",
        "https://www.facebook.com",
        "https://dropbox.com",
        "https://notion.so",
        "https://figma.com",
        "https://canva.com",
        "https://spotify.com",
        "https://claude.ai",
        "https://openai.com",
        "https://anthropic.com",
        "https://yahoo.com",
        "https://bing.com",
        "https://twitch.tv",
        "https://discord.com",
    ],
    "type": ["benign"] * 40
})

df = pd.concat([df, extra_safe], ignore_index=True)
print(f"Total after adding safe URLs: {len(df)}")
print(df["type"].value_counts())

# ── 3. Normalize URLs ─────────────────────────────────────────────
def normalize_url(url):
    url = str(url).strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url

df["url"] = df["url"].apply(normalize_url)

# ── 4. Feature extraction ─────────────────────────────────────────
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
        1 if any(c.isdigit() for c in domain) else 0,
        len(domain),
        len(path),
        url.count("//"),
        has_suspicious,
        is_ip,
        has_suspicious_tld,
    ]

# ── 5. Apply features ─────────────────────────────────────────────
print("\nExtracting features...")
X = df["url"].apply(extract_features).tolist()
y = df["type"].apply(lambda x: 1 if str(x).strip().lower()
                     in ["phishing", "defacement", "malware"]
                     else 0).tolist()

print(f"Malicious: {sum(y)}")
print(f"Safe: {len(y) - sum(y)}")

# ── 6. Balance dataset ────────────────────────────────────────────
print("\nBalancing dataset...")
df_features = pd.DataFrame(X)
df_features["label"] = y

benign = df_features[df_features["label"] == 0]
malicious = df_features[df_features["label"] == 1]

benign_downsampled = resample(
    benign,
    replace=False,
    n_samples=len(malicious),
    random_state=42
)

df_balanced = pd.concat([benign_downsampled, malicious])
df_balanced = df_balanced.sample(frac=1, random_state=42)

X_balanced = df_balanced.drop("label", axis=1).values.tolist()
y_balanced = df_balanced["label"].tolist()

print(f"Balanced dataset: {len(X_balanced)} URLs")

# ── 7. Split ──────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced,
    test_size=0.2,
    random_state=42
)

print(f"Training on {len(X_train)} URLs...")
print(f"Testing on {len(X_test)} URLs...")

# ── 8. Train ──────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train, y_train)
print("\nModel trained successfully")

# ── 9. Accuracy ───────────────────────────────────────────────────
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model accuracy: {accuracy * 100:.2f}%")
print("\nDetailed report:")
print(classification_report(y_test, predictions,
      target_names=["safe", "malicious"]))

# ── 10. Save ──────────────────────────────────────────────────────
joblib.dump(model, "model.pkl")
print("Model saved as model.pkl")
