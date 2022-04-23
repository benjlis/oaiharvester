import os
import requests
from lxml import etree

url = 'https://search.archives.un.org/'
payload = {'metadataPrefix': 'oai_dc',
           'verb': 'ListIdentifiers',
           'set': 'oai:search.archives.un.org:_465279'}
header = {'X-OAI-API-Key': os.getenv('API_KEY')}
ns = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

req = requests.get(url + ';oai?', headers=header, params=payload)
print(req.text)
root = etree.fromstring(bytes(req.text, encoding='utf8'))

for header in root.iterfind('.//oai:header', ns):
    identifier = header.find('oai:identifier', ns).text
    datestamp = header.find('oai:datestamp', ns).text
    print(f'{identifier}, {datestamp}')

# print(root.find('oai:resumptionToken', ns).text)
