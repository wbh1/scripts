#!/bin/env python36
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

import os, shutil, time, logging

# set up logging
def configureLogging():
  logger = logging.getLogger('nagiosimportcleanup.py')
  handler = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s || %(name)s || [%(levelname)s] || %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  logger.setLevel(logging.INFO)
  return logger

# this function gets directories/files & recursively walks the directories for more files
# it returns a List object container files last modified 7+ days ago
def walk(root):
  oldFiles = []
  result = os.walk(root)
  now = time.time()
  sevenDays = 7*24*60*60
  
  for path, _, files in result:
    for file in files:
      full_path = path+"/"+file

      if os.stat(full_path).st_mtime < (now - sevenDays):
        oldFiles.append(full_path)
        log.debug('%s marked for deletion', full_path)

  # Recursively walk each directory it found 
  for _, directory, _ in result:
    root += directory
    walk(root)

  return oldFiles


log = configureLogging()
r = '/usr/local/nagios/etc/import'
files_to_delete = walk(r)

# delete the old files
for file in files_to_delete:
  try:
    os.remove(file)
    log.info('deleted %s', file)
  except Exception as e:
    log.debug(e)
    log.error('could not delete %s', file)
