# sadf.py -- nagios plugin uses sadf output for perf data
# Copyright (C) 2014 Red Hat Inc
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#

from datetime import datetime, timedelta
from glusternagios import utils
import xml.etree.cElementTree as etree

if hasattr(etree, 'ParseError'):
    _etreeExceptions = (etree.ParseError, AttributeError, ValueError)
else:
    _etreeExceptions = (SyntaxError, AttributeError, ValueError)


class SadfException(Exception):
    message = "sadf exception"

    def __init__(self, rc=0, out=(), err=()):
        self.rc = rc
        self.out = out
        self.err = err

    def __str__(self):
        o = '\n'.join(self.out)
        e = '\n'.join(self.err)
        if o and e:
            m = o + '\n' + e
        else:
            m = o or e

        s = self.message
        if m:
            s += '\nerror: ' + m
        if self.rc:
            s += '\nreturn code: %s' % self.rc
        return s


class SadfCmdExecFailedException(SadfException):
    message = "sadf command failed"


class SadfXmlErrorException(SadfException):
    message = "XML error"


def sadfExecCmd(sadfCmd):
    try:
        (rc, out, err) = utils.execCmd(sadfCmd, raw=True)
    except (OSError, ValueError) as e:
        raise SadfCmdExecFailedException(err=[str(e)])

    if rc != 0:
        raise SadfCmdExecFailedException(rc, [out], [err])

    try:
        return etree.fromstring(out)
    except _etreeExceptions:
        raise SadfXmlErrorException(err=[out])


def utcnow():
    return datetime.utcnow()


def getLatestStat(root, interval=1):
    try:
        el = root.findall('host/statistics/timestamp')[-1]
    except (_etreeExceptions + (IndexError,)):
        raise SadfXmlErrorException(err=[etree.tostring(root)])

    d = utils.xml2dict(el)
    statTime = datetime.strptime("%s %s" % (d['timestamp']['date'],
                                            d['timestamp']['time']),
                                 "%Y-%m-%d %H:%M:%S")
    minutes = timedelta(minutes=interval)
    now = utcnow()
    if (now - statTime) <= minutes:
        return d['timestamp']
    else:
        return None


def add_common_args(parser):
    parser.add_argument("-t", "--interval", action="store",
                        type=int,
                        default=1,
                        help="Interval of time(min) older than"
                        " which sadf output in considered stale")
