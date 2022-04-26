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


def get_el_text(el):
    """Returns element text if exists"""
    return '' if el is None else el.text


rows = []
while True:
    try:
        response = requests.get(endpoint, headers=req_header, params=payload)
        if response.status_code == 200:
            root = etree.fromstring(bytes(response.text, encoding='utf8'))
            for record in root.iterfind('.//oai:record', ns):
                header = record.find('oai:header', ns)
                identifier = get_el_text(header.find('oai:identifier', ns)).\
                    split('_')[1]
                datestamp = get_el_text(header.find('oai:datestamp', ns))
                setspec = get_el_text(header.find('oai:setSpec', ns)).\
                    split('_')[1]
                metadata = record.find('oai:metadata/oai_dc:dc', ns)
                title = get_el_text(metadata.find('dc:title', ns))
                creator = get_el_text(metadata.find('dc:creator', ns))
                description = get_el_text(metadata.find('dc:description', ns))
                rights = get_el_text(metadata.find('dc:rights', ns))
                identifiers = metadata.findall('dc:identifier', ns)
                if len(identifiers) >= 2:
                    id1 = get_el_text(identifiers[0])
                    id2 = get_el_text(identifiers[1])
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
