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
           'set': 'oai:search.archives.un.org:_465279'
           }
# payload = {'verb': 'GetRecord',
#            'metadataPrefix': 'oai_dc',
#            'identifier': 'oai:search.archives.un.org:_468300'}
req_header = {'X-OAI-API-Key': os.getenv('API_KEY')}
ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
      'dc': 'http://purl.org/dc/elements/1.1/',
      'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
      'atom': 'http://www.w3.org/2005/Atom'}


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
                # check for PDF attachment
                about = record.find('oai:about', ns)
                if about is None:
                    doc = 'N'
                    pdf_url = jpg_url = ''
                else:
                    doc = 'Y'
                    urls = about.findall('atom:feed/atom:entry/atom:link', ns)
                    if len(urls) >= 2:
                        pdf_url = urls[0].attrib['href']
                        jpg_url = urls[1].attrib['href']
                rows.append([identifier, datestamp, setspec, title, creator,
                             description, rights, id1, id2, doc, pdf_url,
                             jpg_url])
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: \
{len(rows)} items processed')
            resumption_token = get_el_text(root.find('.//oai:resumptionToken',
                                                     ns))
            if resumption_token:
                payload = {'verb': 'ListRecords',
                           'resumptionToken': resumption_token}
            else:      # No resumption_token means no more no data
                break
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
          'doc', 'pdf_url', 'jpg_url']
with open(CSV_FILENAME, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)
