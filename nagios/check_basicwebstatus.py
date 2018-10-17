#
# The MIT License (MIT)
#
# Copyright (c) 2018 William Hegedus <wbhegedus@liberty.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# https://www.liberty.edu/upay-postback/status

import argparse

# Define Nagios statuses
status = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN']

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', required=True, help='Set the URL to check')
args = parser.parse_args()

# Set the URL to check
url = args.url

# Get the page content
import requests, json
r = requests.get(url)
raw = r.text
json_out = json.loads(raw)

# Evaluate page content
if json_out['status'] == "OK":
    exit_code = 0
else:
    exit_code = 2

# Exit based on content evaluation
print(status[exit_code] + " -- Request returned:\n" + raw)
exit(exit_code)
