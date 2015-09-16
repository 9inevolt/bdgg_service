import datetime
import json
import os
import re
import time
from calendar import timegm

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

class LogSystem:
    def __init__(self, path='/'):
        self.today = datetime.datetime.now()

    @inlineCallbacks
    def GetLastLines(self, username, lines = 1):    #case-insensitive, searches all months, returns list of lines or None
        url = str('http://overrustlelogs.net/api/v1/stalk/Destinygg%%20chatlog/%s.json?limit=%d' % (username, lines))
        data = yield getPage(url)
        stalk_json = json.loads(data)
        if 'lines' in stalk_json:
            returnValue(stalk_json['lines'])
        else:
            returnValue(None)

    def ParseTimestamps(self, lines):  #returns timestamps for lines
        out = []
        for line in lines:
            if isinstance(line, int):
                dtt = time.gmtime(line)
            else:
                type = None
                match = re.search('(\w\w\w \d?\d \d?\d:\d\d:\d\d UTC)', line)
                if not match:
                    match = re.search('(\w\w\w \d?\d \d\d\d\d \d?\d:\d\d:\d\d UTC)', line)
                    type = 1
                if not match:
                    match = re.search('(\[\d\d/\d\d/\d\d\d\d \d?\d:\d\d:\d\d (?:AM|PM)\])', line)
                    type = 2
                if not match:
                    match = re.search('(\[\d\d\d\d-\d\d-\d\d \d?\d:\d\d:\d\d UTC\])', line)
                    type = 3

                if match:
                    if not type:
                        addyear = str(self.today.year) + ' ' + match.group(1)
                        dtt = time.strptime(addyear, '%Y %b %d %H:%M:%S UTC')
                    elif type == 1:
                        dtt = time.strptime(match.group(1), '%b %d %Y %H:%M:%S UTC')
                    elif type == 2:
                        dtt = time.strptime(match.group(1), '[%m/%d/%Y %I:%M:%S %p]')
                    elif type == 3:
                        dtt = time.strptime(match.group(1), '[%Y-%m-%d %H:%M:%S UTC]')

            out.append(timegm(dtt))
        return out
