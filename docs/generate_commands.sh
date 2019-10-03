#!/bin/bash

commands="$(python ../pkpass.py -h | grep '{.*}' | head -1 | tr -d '[:space:]{}')"
IFS=","

cat << EOF > /tmp/test
Commands
========
The Commands can be listed out by passing the help flag to pkpass as seen below

EOF

{
    echo ".. code-block:: bash

"
    python ../pkpass.py -h | awk '{ print "    "$0 }'
} >> /tmp/test

for com in $commands; do
    {
echo "
${com^}"
awk "BEGIN{for(c=0;c<${#com};c++) printf \"-\"}"
echo "
Blurb

.. code-block:: bash
"
    python ../pkpass.py "$com" -h | awk '{ print "    "$0 }'
} >> /tmp/test
done
