import os, tempfile, subprocess
from xml.dom.minidom import parse
import re

class Xe:
    _tempdir = None
    def _get_platform_info(self):
        curdir = os.curdir
        os.chdir(self._tempdir)
        p = subprocess.Popen(["xobjdump --split %s"%self.path], shell=True, 
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        p.wait()
        xn = parse("%s/platform_def.xn"%self._tempdir)
        self._core_map = {}
        self.cores = []
        for node in xn.getElementsByTagName("Node"):
            cm = {}
            for core in node.getElementsByTagName("Core"):
                self._core_map[node.getAttribute("Id"),
                               core.getAttribute("Number")] = \
                  core.getAttribute("Reference")
                self.cores.append(core.getAttribute("Reference"))
        os.chdir(curdir)

    def _get_symtab(self):
        process = subprocess.Popen(["xobjdump -t %s"%self.path], shell=True, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        current_core = None
        symtab = {}
        while True:
            line = process.stdout.readline()
            if (line == ''):
                break
            m = re.match(r'Loadable.*for .*node \"(\d*)\", core (\d*)', line)
            if m:
                (node_num, core_num) = m.groups(0)
                current_core = self._core_map[node_num, core_num]
            m = re.match(r'(0x[0-9a-fA-F]*).....([^ ]*) *(0x[0-9a-fA-F]*) (.*)$', line)
            if m and current_core != None:
                (address, section, size, name) = m.groups(0)
                if section != '*ABS*':
                    address = int(address,0)
                    symtab[current_core, name] = address
        self.symtab = symtab


    def __init__(self, path):
        if not os.path.isfile(path):
            raise IOError("Cannot find file: %s"%path)
        self.path = os.path.abspath(path)
        self._symtab = {}
        self._tempdir = tempfile.mkdtemp()
        self._get_platform_info()
        self._get_symtab()
    
    def __del__(self):
        if self._tempdir != None:
            for root, dirs, files in os.walk(self._tempdir, topdown=False):
                for f in files:
                    p = os.path.join(root,f)
                    os.remove(p)
                for d in dirs:
                    p = os.path.join(root,d)
                    os.rmdir(p)
            os.rmdir(self._tempdir)


