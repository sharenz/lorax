import sys

import os
import commands
import re


class LDD(object):
    def __init__(self, libroot='/'):
        f = open('/usr/bin/ldd', 'r')
        for line in f.readlines():
            line = line.strip()
            if line.startswith('RTLDLIST='):
                rtldlist, sep, ld_linux = line.partition('=')
                break
        f.close()

        self._ldd = '%s --list --library-path %s' % (ld_linux, libroot)
        self._deps = set()

    def getDeps(self, filename):
        rc, output = commands.getstatusoutput('%s %s' % (self._ldd, filename))

        if rc:
            return

        lines = output.splitlines()
        for line in lines:
            line = line.strip()

            m = re.match(r'^[a-zA-Z0-9.]*\s=>\s(?P<lib>[a-zA-Z0-9./]*)\s\(0x[0-9a-f]*\)$', line)
            if m:
                lib = m.group('lib')
                if lib not in self._deps:
                    self._deps.add(lib)
                    self.getDeps(lib)

    def getLinks(self):
        targets = set()
        for lib in self._deps:
            if os.path.islink(lib):
                targets.add(os.path.realpath(lib))

        self._deps.update(targets)

    @property
    def deps(self):
        return self._deps


if __name__ == '__main__':
    ldd = LDD(libroot=sys.argv[2])
    ldd.getDeps(sys.argv[1])
    ldd.getLinks()

    for dep in ldd.deps:
        print dep
