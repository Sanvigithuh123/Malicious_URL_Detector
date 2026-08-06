import requests

# known URLs with expected results
test_urls = [
    # should be SAFE
    ("https://google.com",           "safe"),
    ("https://github.com",           "safe"),
    ("https://wikipedia.org",        "safe"),
    ("https://stackoverflow.com",    "safe"),
    ("https://youtube.com",          "safe"),
    ("https://reddit.com",           "safe"),

    # should be MALICIOUS
    ("http://paypal-secure-login.tk/verify?id=123",        "malicious"),
    ("http://free-bitcoin-generator.net/claim?user=you",   "malicious"),
    ("http://apple-id-locked.ml/unlock?token=abc",         "malicious"),
    ("http://login-facebook-secure.weebly.com/account",    "malicious"),
    ("http://192.168.1.1/admin/login.php?steal=true",      "malicious"),
    ("http://secure-paypal.com-login.xyz/account",         "malicious"),
    ("http://gmail.com.phishing-login.tk",                 "malicious"),
    ("http://signin.eby.de.zukruygxctzmmqi.civpro.co.za",  "malicious"),
]

print(f"{'EXPECTED':12} {'GOT':12} {'SCORE':8} {'CORRECT':8}  URL")
print("─" * 90)

correct = 0
total = len(test_urls)

for url, expected in test_urls:
    try:
        response = requests.post(
            "http://localhost:5000/predict",
            json={"url": url}
        )
        result = response.json()
        got = result["label"]
        score = result["score"]
        is_correct = got == expected

        if is_correct:
            correct += 1
            tick = "✓"
        else:
            tick = "✗"

        print(f"{expected:12} {got:12} {score:6.1f}%   {tick}      {url}")

    except Exception as e:
        print(f"ERROR: {e}")

print("─" * 90)
print(f"\nResult: {correct}/{total} correct ({correct/total*100:.1f}% accuracy on test URLs)")

if correct == total:
    print("✓ Model is working perfectly")
elif correct >= total * 0.8:
    print("~ Model is working well but has some false positives/negatives")
else:
    print("✗ Model needs improvement")
