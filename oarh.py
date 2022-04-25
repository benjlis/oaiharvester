import os
import requests
import time
from lxml import etree
from datetime import datetime
import csv
import traceback

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
    try:
        response = requests.get(endpoint, headers=req_header, params=payload)
        if response.status_code == 200:
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
                about = 'N' if record.find('oai:about', ns) is None else 'Y'
                rows.append([identifier, datestamp, setspec, title, creator,
                            description, rights, id1, id2, about])
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: \
{len(rows)} items processed')
            payload = {'verb': 'ListRecords',
                       'resumptionToken': root.find('.//oai:resumptionToken',
                                                    ns).text}
        else:
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: \
{response.status_code} http status')
        time.sleep(REQUEST_SLEEP)
    except (Exception, KeyboardInterrupt):
        traceback.print_exc()
        print('Exiting processing loop')
        break

print(f'Saving to {CSV_FILENAME}')
fields = ['oai_id', 'oai_datestamp', 'oai_set', 'dc_title', 'dc_creator',
          'dc_description', 'dc_rights', 'dc_identifier1', 'dc_identifier2',
          'about']
with open(CSV_FILENAME, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)
