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
import re
import sys

from servicenow_email import SNEmail

### Define variables ###
subject = "An IFEP Component is Stopped"
fromaddr = "blackhole@liberty.edu"
toaddr = "liberty@service-now.com"


def configureLogging():
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler("/var/log/scripts/IFEPEventHandler.log")
    formatter = logging.Formatter(
        "%(asctime)s || [%(levelname)s] || %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


def sendEmail():
    email = SNEmail(toaddr, fromaddr, subject)

    body = (
        "Item: Server Maintenance \n"
        "Assignment group: System Operations - OCC \n"
        "Requested for: Nagios XI \n"
        "Priority: 1\n"
        "\n%s \n"
        "One of the IFEP services from https://eprocurement1.liberty.edu/default-app/jsp/frames-index.jsp is reporting as down.\n"
        "If this is occurring during Banner Downtime, IFEP services will need to be restarted after downtime is completed.\n"
        "If this is not during Banner Downtime, please attempt to restart services. If it fails to come back up, convert this TKT to an incident and notify GenSYS \n"
        "For more information, please refer to: \n"
        "https://nocwiki.liberty.edu:8443/pages/viewpage.action?pageId=40861912 \n"
    ) % serviceSummary

    email.setBody(body)
    email.send()


########################################
############### HANDLER ################
########################################

# Create a logger first thing
LOG = configureLogging()

# Make sure there are the right number of arguments from Nagios
try:
    serviceState = sys.argv[1]
    serviceStateType = sys.argv[2]
    serviceOutput = sys.argv[3:]
    serviceSummary = " ".join(serviceOutput)
except IndexError as e:
    LOG.critical(e)
    sys.exit(1)

# Send the email if the state is critical and hard
if serviceState == "CRITICAL":
    if serviceStateType == "HARD":
        # Check if the alert is because of a timeout, using regex matchers
        TIMEOUT_REGEX = re.compile(r".*Timed Out On Worker:.*")
        if TIMEOUT_REGEX.match(serviceSummary):
            LOG.info(
                "Not creating a TKT since the check is timing out instead of failing")
        else:
            sendEmail()
            LOG.info("Sent email to {0}".format(toaddr))
    else:
        LOG.debug("Service state is critical but state type is not hard.")
else:
    LOG.debug(
        "Service state is {0}. Nothing to be done.".format(serviceState)
    )
