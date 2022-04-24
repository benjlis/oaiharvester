import os
import requests
import time
from lxml import etree
import csv

# define OAI details
endpoint = 'https://search.archives.un.org/;oai?'
payload = {'verb': 'ListIdentifiers',
           'metadataPrefix': 'oai_dc',
           'set': 'oai:search.archives.un.org:_465279'}
req_header = {'X-OAI-API-Key': os.getenv('API_KEY')}
ns = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

rows = []
response = requests.get(endpoint, headers=req_header, params=payload)
root = etree.fromstring(bytes(response.text, encoding='utf8'))
payload = {'verb': 'ListIdentifiers'}
for i in range(4):
    for header in root.iterfind('.//oai:header', ns):
        identifier = header.find('oai:identifier', ns).text.split('_')[1]
        datestamp = header.find('oai:datestamp', ns).text
        setspec = header.find('oai:setSpec', ns).text.split('_')[1]
        rows.append([identifier, datestamp, setspec])
    payload['resumptionToken'] = root.find('.//oai:resumptionToken', ns).text
    response = requests.get(endpoint, headers=req_header, params=payload)
    print(response)
    print(response.headers)
    time.sleep(60)
    # print(response.text)
    root = etree.fromstring(bytes(response.text, encoding='utf8'))

# generate CSV file
filename = 'oai.csv'
fields = ['oai_id', 'oai_datestamp', 'oai_set']
with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)

# print(root.find('oai:resumptionToken', ns).text)
