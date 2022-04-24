import os
import requests
import time
from lxml import etree
from datetime import datetime
import csv

CSV_FILENAME = 'oahr.csv'
REQUEST_SLEEP = 5        # sleep between API requests (seconds)

# define OAI details
endpoint = 'https://search.archives.un.org/;oai?'
payload = {'verb': 'ListIdentifiers',
           'metadataPrefix': 'oai_dc',
           'set': 'oai:search.archives.un.org:_465279'}
req_header = {'X-OAI-API-Key': os.getenv('API_KEY')}
ns = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

rows = []
while True:
    response = requests.get(endpoint, headers=req_header, params=payload)
    if response.status_code != 200:
        print(f'{response.status_code} status, exiting API call loop')
        break
    root = etree.fromstring(bytes(response.text, encoding='utf8'))
    for header in root.iterfind('.//oai:header', ns):
        identifier = header.find('oai:identifier', ns).text.split('_')[1]
        datestamp = header.find('oai:datestamp', ns).text
        setspec = header.find('oai:setSpec', ns).text.split('_')[1]
        rows.append([identifier, datestamp, setspec])
    response = requests.get(endpoint, headers=req_header, params=payload)
    print(f'{datetime.now()}: {len(rows)} items processed, http status:\
 {response.status_code}')
    payload = {'verb': 'ListRecords',
               'resumptionToken': root.find('.//oai:resumptionToken', ns).text}
    time.sleep(REQUEST_SLEEP)

print('Saving to {CSV_FILENAME}')
fields = ['oai_id', 'oai_datestamp', 'oai_set']
with open(CSV_FILENAME, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)

# print(root.find('oai:resumptionToken', ns).text)
