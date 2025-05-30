import json 

with open('data/chunks/fin_chunks.json', 'r') as f:
    findata = json.load(f)

with open('data/chunks/news_chunks.json', 'r') as f:
    newsdata = json.load(f)

# normalize the data 
def format_fin_records(record):
    return {
        "text": record["text"],  # already summarized
        "metadata": {
            "type": "financials",
            "date": record["metadata"]["date"],
            "quarter": record["metadata"].get("quarter"),
            "year": record["metadata"].get("year"),
            "ticker": record["metadata"].get("ticker", "NOG"),
            "source": record["metadata"].get("source", "combined"),
            "annual_metrics": record["metadata"].get("annual_metrics", {})
        }
    }

def format_news_records(record):
        return {
        "text": f"{record['text']} - {record['metadata']['date']}",
        "metadata": {
            "type": "news",
            "date": record['metadata']["date"],
            "source": record['metadata'].get("source", "unknown"),
            "ticker": "NOG"
        }
    }

# combine 
combined = []

for rec in findata:
     combined.append(format_fin_records(rec))
    
for rec in newsdata:
     combined.append(format_news_records(rec))
    
# write to the jsonl file 
with open('corpus.jsonl', 'w') as f:
     for doc in combined:
          f.write(json.dumps(doc) + '\n')

print('Combined corpus created!')