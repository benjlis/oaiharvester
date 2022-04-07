# Sets
./cae.sh ListSets > set.xml
# Moon Fond
./cae.sh GetRecord\&identifier=oai:search.archives.un.org:_465279\&metadataPrefix=oai_dc > moon.xml
# Moon List IDs
./cae.sh ListIdentifiers\&set=oai:search.archives.un.org:_465279\&metadataPrefix=oai_dc > moon-list.xml
# Moon List records
./cae.sh ListRecords\&set=oai:search.archives.un.org:_465279\&metadataPrefix=oai_dc > moon-records.xml
# Moon List records range
./cae.sh ListRecords\&set=oai:search.archives.un.org:_465279\&from=2018-08-02\&until=2018-08-04\&metadataPrefix=oai_dc > moon-records-2009.xml
