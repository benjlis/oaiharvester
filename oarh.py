import os
import requests
import time
from lxml import etree
from datetime import datetime
import csv

CSV_FILENAME = 'oahr.csv'
REQUEST_SLEEP = 60        # sleep between API requests (seconds)

# define OAI details
endpoint = 'https://search.archives.un.org/;oai?'
payload = {'verb': 'ListRecords',
           'metadataPrefix': 'oai_dc',
           'set': 'oai:search.archives.un.org:_465279'}
req_header = {'X-OAI-API-Key': os.getenv('API_KEY')}
ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
      'dc': 'http://purl.org/dc/elements/1.1/',
      'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'}

rows = []
while True:
    response = requests.get(endpoint, headers=req_header, params=payload)
    if response.status_code != 200:
        print(f'{response.status_code} status, exiting API call loop')
        break
    root = etree.fromstring(bytes(response.text, encoding='utf8'))
    for record in root.iterfind('.//oai:record', ns):
        header = record.find('oai:header', ns)
        identifier = header.find('oai:identifier', ns).text.split('_')[1]
        datestamp = header.find('oai:datestamp', ns).text
        setspec = header.find('oai:setSpec', ns).text.split('_')[1]
        metadata = record.find('oai:metadata/oai_dc:dc', ns)
        title = metadata.find('dc:title', ns).text
        creator = metadata.find('dc:creator', ns).text
        description_el = metadata.find('dc:description', ns)
        description = None
        if description_el is not None:
            description = description_el.text
        rights = metadata.find('dc:rights', ns).text
        identifiers = metadata.findall('dc:identifier', ns)
        id1 = identifiers[0].text
        id2 = identifiers[1].text
        about = 'N' if header.find('oai:about', ns) is None else 'Y'
        rows.append([identifier, datestamp, setspec, title, creator,
                     description, rights, id1, id2, about])
    response = requests.get(endpoint, headers=req_header, params=payload)
    print(f'{datetime.now()}: {len(rows)} items processed, http status:\
 {response.status_code}')
    payload = {'verb': 'ListRecords',
               'resumptionToken': root.find('.//oai:resumptionToken', ns).text}
    time.sleep(REQUEST_SLEEP)

print(f'Saving to {CSV_FILENAME}')
fields = ['oai_id', 'oai_datestamp', 'oai_set', 'dc_title', 'dc_creator',
          'dc_description', 'dc_rights', 'about']
with open(CSV_FILENAME, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)

# print(root.find('oai:resumptionToken', ns).text)