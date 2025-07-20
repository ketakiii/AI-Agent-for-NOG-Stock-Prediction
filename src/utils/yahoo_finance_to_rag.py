import json 
import csv

ticker = 'NOG'

def format_volume(vol):
    return f'{int(float(vol)):,}'

def format_price(price):
    return f'{float(price):.2f}'

inputcsv = 'data/NOG_2years.csv'
outputjson = 'data/chunks/corpus.jsonl'
jsonlist = []

def yf_csv_to_json():
    with open(inputcsv, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row['Date']
            open_price = row['Open']
            close_price = row['Close']
            high = row['High']
            low = row['Close']
            volume = row['Volume']

            text = (f'On {date}, {ticker} opened at {open_price}, closed at {close_price} ,'
                    f'with a high of {high} and low of {low}. Volume was {volume}')
            
            jsonobj = {
                'text':text,
                'metadata': {
                    'type':'price',
                    'date':date,
                    'ticker':ticker
                }
            }
            with open(outputjson, 'a') as out:  # open the file for appending
                out.write(json.dumps(jsonobj) + '\n') 
    
    print('Done with the NOG price data appending!')

yf_csv_to_json()