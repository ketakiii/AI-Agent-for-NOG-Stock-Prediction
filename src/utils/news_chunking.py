import csv
import json

input_file = "data/NOG_news_2years.csv"
output_file = "data/chunks/news_chunks.json"

news_docs = []
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)  # Use DictReader to access by column name
    for row in reader:
        # Use the correct column names from your CSV
        date = row['date']
        title = row['title']
        description = row['description']
        url = row['url']
        publisher = row['publisher']
        content = row['content']
        
        # Use content if available, otherwise use description
        text = content if content and content != 'nan' else description
        
        if text and text != 'nan' and len(text.strip()) > 10:  # Only add if we have meaningful text
            news_docs.append({
                "text": text.strip(),
                "metadata": {
                    "type": "news",
                    "date": date.strip(),
                    "title": title.strip(),
                    "publisher": publisher.strip(),
                    "url": url.strip()
                }
            })

print(f"Created {len(news_docs)} news documents")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(news_docs, f, indent=4)
