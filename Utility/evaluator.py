import pandas as pd
import tldextract
from google.colab import drive

drive.mount("/content/drive", force_remount=True)

domain_categories = {
    "technology": [
        "addtoany", "adobe", "computerhope", "computerlanguage", "eurid", "google",
        "mediawiki", "merlot", "oercommons", "pc"
    ],
    "business": [
        "hbr", "philadelphiabusinesslist"
    ],
    "politics": [
        "newpol"
    ],
    "history": [
        "historic-uk", "newworldencyclopedia", "worldhistory", "ushistory"
    ]
}

results = {}
total = 0
total_urls = 0

csv_file = "/content/drive/MyDrive/KAIST/Spider1/results.csv"
df = pd.read_csv(csv_file)

if "true_label" not in df.columns:
    df["true_label"] = None

for i, row in df.iterrows():
    domain = tldextract.extract(row["link"]).domain
    total_urls += 1
    if row["processed"] != "Yes":
        continue

    total += 1
    label_str = row["label"]
    first_label = label_str.split(',')[0].split(':')[0][2:].strip()

    matched = False
    for label, domains in domain_categories.items():
        if domain in domains:
            df.at[i, "true_label"] = label
            if label not in results:
                results[label] = {"match": 0, "mismatch": 0, "count": 0}
            results[label]["count"] += 1
            if first_label == label:
                results[label]["match"] += 1
            else:
                results[label]["mismatch"] += 1
            matched = True
            break

    if not matched:
        df.at[i, "true_label"] = "N/A"

print(f"Total processed: {total}")
print(f"Total URLs: {total_urls}\n")
for label, stats in results.items():
    TP = stats["match"]
    FP = stats["mismatch"]
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0

    print(f"[{label.upper()}] matched: {stats['match']} / {stats['count']} | mismatch: {stats['mismatch']} | 🎯 Precision: {precision:.2f}")
