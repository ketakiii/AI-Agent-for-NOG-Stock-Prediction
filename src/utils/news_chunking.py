import csv
import json

input_file = "data/NOG_news_2years.csv"
output_file = "data/chunks/news_chunks.json"

news_docs = []
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        date, title, text, url, source = row
        news_docs.append({
            "text": text.strip(),
            "metadata": {
                "type": "news",
                "date": date.strip(),
                "title": title.strip(),
                "source": source.strip(),
                "url": url.strip()
            }
        })

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(news_docs, f, indent=4)
