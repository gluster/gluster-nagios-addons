#
# Copyright 2014 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

## This framework is mostly copied from vdsm test framework

import logging
import sys
import os
import unittest
import re
import shutil
import tempfile
from contextlib import contextmanager
from glusternagios import utils
# Monkey patch pthreading in necessary
if sys.version_info[0] == 2:
    # as long as we work with Python 2, we need to monkey-patch threading
    # module before it is ever used.
    import pthreading
    pthreading.monkey_patch()
from nose import config
from nose import core
from nose import result

from testValidation import SlowTestsPlugin, StressTestsPlugin


class TermColor(object):
    black = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37


def colorWrite(stream, text, color):
    if os.isatty(stream.fileno()) or os.environ.get("NOSE_COLOR", False):
        stream.write('\x1b[%s;1m%s\x1b[0m' % (color, text))
    else:
        stream.write(text)


@contextmanager
def temporaryPath(perms=None, data=None):
    fd, src = tempfile.mkstemp()
    if data is not None:
        f = os.fdopen(fd, "wb")
        f.write(data)
        f.flush()
        f.close()
    else:
        os.close(fd)
    if perms is not None:
        os.chmod(src, perms)
    try:
        yield src
    finally:
        os.unlink(src)


@contextmanager
def namedTemporaryDir():
    tmpDir = tempfile.mkdtemp()
    try:
        yield tmpDir
    finally:
        shutil.rmtree(tmpDir)


# FIXME: This is a forward port of the assertRaises from python
#        2.7, remove when no longer supporting earlier versions
class _AssertRaisesContext(object):
    """A context manager used to implement TestCase.assertRaises* methods."""

    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "{0} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        self.exception = exc_value  # store for later retrieval
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                                        (expected_regexp.pattern,
                                         str(exc_value)))
        return True


# FIXME: This is a forward port of the assertIn from python
#        2.7, remove when no longer supporting earlier versions
def safe_repr(obj, short=False):
    _MAX_LENGTH = 80
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'


class PluginsTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)

    def retryAssert(self, *args, **kwargs):
        '''Keep retrying an assertion if AssertionError is raised.
           See function utils.retry for the meaning of the arguments.
        '''
        return utils.retry(expectedException=AssertionError, *args, **kwargs)

    # FIXME: This is a forward port of the assertRaises from python
    #        2.7, remove when no longer supporting earlier versions
    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)

    # FIXME: This is a forward port of the assertIn from python
    #        2.7, remove when no longer supporting earlier versions
    def assertIn(self, member, container, msg=None):
        """
        Just like self.assertTrue(a in b), but with a nicer default message.
        """
        if member not in container:
            if msg is None:
                msg = '%s not found in %s' % (safe_repr(member),
                                              safe_repr(container))
            raise self.failureException(msg)

    # FIXME: This is a forward port of the assertNotIn from python
    #        2.7, remove when no longer supporting earlier versions
    def assertNotIn(self, member, container, msg=None):
        """
        Just like self.assertTrue(a not in b), but with a nicer default message
        """
        if member in container:
            if msg is None:
                msg = '%s unexpectedly found in %s' % (safe_repr(member),
                                                       safe_repr(container))
            raise self.failureException(msg)


class PluginsTestResult(result.TextTestResult):
    def __init__(self, *args, **kwargs):
        result.TextTestResult.__init__(self, *args, **kwargs)
        self._last_case = None

    def getDescription(self, test):
        return str(test)

    def _writeResult(self, test, long_result, color, short_result, success):
        if self.showAll:
            colorWrite(self.stream, long_result, color)
            self.stream.writeln()
        elif self.dots:
            self.stream.write(short_result)
            self.stream.flush()

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self._writeResult(test, 'OK', TermColor.green, '.', True)

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self._writeResult(test, 'FAIL', TermColor.red, 'F', False)

    def addSkip(self, test, reason):
        # 2.7 skip compat
        from nose.plugins.skip import SkipTest
        if SkipTest in self.errorClasses:
            storage, label, isfail = self.errorClasses[SkipTest]
            storage.append((test, reason))
            self._writeResult(test, 'SKIP : %s' % reason, TermColor.blue, 'S',
                              True)

    def addError(self, test, err):
        stream = getattr(self, 'stream', None)
        ec, ev, tb = err
        try:
            exc_info = self._exc_info_to_string(err, test)
        except TypeError:
            # 2.3 compat
            exc_info = self._exc_info_to_string(err)
        for cls, (storage, label, isfail) in self.errorClasses.items():
            if result.isclass(ec) and issubclass(ec, cls):
                if isfail:
                    test.passed = False
                storage.append((test, exc_info))
                # Might get patched into a streamless result
                if stream is not None:
                    if self.showAll:
                        message = [label]
                        detail = result._exception_detail(err[1])
                        if detail:
                            message.append(detail)
                        stream.writeln(": ".join(message))
                    elif self.dots:
                        stream.write(label[:1])
                return
        self.errors.append((test, exc_info))
        test.passed = False
        if stream is not None:
            self._writeResult(test, 'ERROR', TermColor.red, 'E', False)

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        current_case = test.test.__class__.__name__

        if self.showAll:
            if current_case != self._last_case:
                self.stream.writeln(current_case)
                self._last_case = current_case

            self.stream.write(
                '    %s' % str(test.test._testMethodName).ljust(60))
            self.stream.flush()


class PluginsTestRunner(core.TextTestRunner):
    def __init__(self, *args, **kwargs):
        core.TextTestRunner.__init__(self, *args, **kwargs)

    def _makeResult(self):
        return PluginsTestResult(self.stream,
                                 self.descriptions,
                                 self.verbosity,
                                 self.config)

    def run(self, test):
        result_ = core.TextTestRunner.run(self, test)
        return result_


def run():
    argv = sys.argv
    stream = sys.stdout
    verbosity = 3
    testdir = os.path.dirname(os.path.abspath(__file__))

    conf = config.Config(stream=stream,
                         env=os.environ,
                         verbosity=verbosity,
                         workingDir=testdir,
                         plugins=core.DefaultPluginManager())
    conf.plugins.addPlugin(SlowTestsPlugin())
    conf.plugins.addPlugin(StressTestsPlugin())

    runner = PluginsTestRunner(stream=conf.stream,
                               verbosity=conf.verbosity,
                               config=conf)

    sys.exit(not core.run(config=conf, testRunner=runner, argv=argv))


def findRemove(listR, value):
    """used to test if a value exist, if it is, return true and remove it."""
    try:
        listR.remove(value)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    run()
