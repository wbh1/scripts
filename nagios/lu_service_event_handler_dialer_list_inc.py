#! /usr/bin/env python3
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

import logging
import sys

from servicenow_email import SNEmail

### Define variables ###
subject = "WHPRD Dialer Import(s) Failed"
fromaddr = "blackhole@liberty.edu"
toaddr = "liberty@service-now.com"


def configureLogging():
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler("/var/log/scripts/DialerListEventHandler.log")
    formatter = logging.Formatter("%(asctime)s || [%(levelname)s] || %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def sendEmail():
    email = SNEmail(toaddr, fromaddr, subject)

    body = (
        "Item: Server Maintenance \n"
        "Assignment group: System Operations - OCC \n"
        "Requested for: Nagios XI \n"
        "Priority: 1\n"
        "\n%s \n"
        "Please follow instructions located at: \n"
        "https://nocwiki.liberty.edu:8443/display/NOC/WHPRD+-+Monitoring#WHPRD-Monitoring-DialerImport \n"
        "Convert to an INC before sending to ADS Communications"
    ) % serviceSummary

    email.setBody(body)
    email.send()


########################################
############### HANDLER ################
########################################

# Create a logger first thing
log = configureLogging()

# Make sure there are the right number of arguments from Nagios
try:
    serviceState = sys.argv[1]
    serviceStateType = sys.argv[2]
    serviceOutput = sys.argv[3:]
    serviceSummary = " ".join(serviceOutput)
except Exception as e:
    log.critical(e)
    sys.exit(1)

# Send the email if the state is critical and hard
if serviceState == "CRITICAL":
    if serviceStateType == "HARD":
        sendEmail()
        log.info("Sent email to {0}".format(toaddr))
    else:
        log.debug("Service state is critical but state type is not hard.")
else:
    log.critical(
        "Service state is not critical. This event handler shouldn't have been called"
    )
