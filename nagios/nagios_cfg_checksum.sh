#!/bin/bash
# Copyright 2018 William Hegedus <will@liberty.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentatio                                                                                                                                                    n files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy                                                                                                                                                    , modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Sof                                                                                                                                                    tware is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Soft                                                                                                                                                    ware.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARR                                                                                                                                                    ANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT                                                                                                                                                     HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING                                                                                                                                                     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# directory where the .prom file will be output
TEXTFILE_COLLECTOR_DIR=/opt/prometheus/textfile_collector

# file hashes as of 09/13/2018
EXPECTED_RESOURCE_HASH="1e14c48a0c3b5614eca30cf7fb23fb52"
EXPECTED_NAGIOS_HASH="89869eb7c4b114f32ebcb8bac20c7c42"

# calculate the current file hashes
ACTUAL_RESOURCE_HASH=`md5sum /usr/local/nagios/etc/resource.cfg | awk {'print$1}'`
ACTUAL_NAGIOS_HASH=`md5sum /usr/local/nagios/etc/nagios.cfg | awk {'print$1}'`


# Compare the hashes
if [ $EXPECTED_RESOURCE_HASH = $ACTUAL_RESOURCE_HASH ]; then
  RESOURCE=1
else
  RESOURCE=0
fi

if [ $EXPECTED_NAGIOS_HASH = $ACTUAL_NAGIOS_HASH ]; then
  NAGIOS=1
else
  NAGIOS=0
fi

# Output the results in a format that prometheus can understand to a temp file
cat << EOF > "$TEXTFILE_COLLECTOR_DIR/confighashes.prom.$$"
nagios_config_hash{file="resource.cfg"} $RESOURCE
nagios_config_hash{file="nagios.cfg"} $NAGIOS
EOF

# move the temp file to the actual file -- the temp file prevents a half-written file from being collected
mv "$TEXTFILE_COLLECTOR_DIR/confighashes.prom.$$" \
  "$TEXTFILE_COLLECTOR_DIR/confighashes.prom"

