from backend.features import extract_features

urls = [
    "https://www.youtube.com/",
    "https://github.com/",
    "https://www.google.com/"
]

print(f"{'URL':<30} | {'Features'}")
print("-" * 100)

for url in urls:
    feats = extract_features(url)
    print(f"{url:<30} | {feats}")
