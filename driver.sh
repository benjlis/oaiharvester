# Cycles through all verbs in the OAI API.
verbs="Identify ListMetadataFormats"
for v in ${verbs}
do
    echo "${v}:"
    ${HHOME}/cae.sh $v
    echo
done
