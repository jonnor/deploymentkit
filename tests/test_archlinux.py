import unittest, os, sys

import deploymentkit
from deploymentkit.core import recipe, target, generator
from deploymentkit.backends import linux, archlinux

import utils

pkgbuild_attribute = archlinux.pkgbuild_attribute

class TestParsePkgbuild(unittest.TestCase):
    """Test that the PKGBUILD parser used for testing works."""
    
    def setUp(self):
        self.file = open(utils.get_testdata_file('PKGBUILD'))
        self.str = self.file.read()

    def test_pkgname(self):
        self.assertEqual(pkgbuild_attribute(self.str, 'pkgname'), 
            'ora-thumbnailer-kde')

    def test_pkgver(self):
        self.assertEqual(pkgbuild_attribute(self.str, 'pkgver'), '0.1.0')

    def test_pkgdesc(self):
        self.assertEqual(pkgbuild_attribute(self.str, 'pkgdesc'), 
                '\"OpenRaster thumbnailer for KDE (Dolphin/Kio)\"')

    def test_depends(self):
        self.assertEqual(pkgbuild_attribute(self.str, 'depends'), 
                '(\'pygtk\' \'gconf\')')

    def tearDown(self):
        self.file.close()

input_metadata = {
    'Name': 'testpackage',
    'Version': '0.0.1',
    'ReleaseVersion': 1,
    'BriefDescription': 'This is a test package',
    'URL': "http://www.example.com/testpackage",
    'Licenses': ['GPL', 'custom'],
    'BuildSystemType': 'distutils',
    'ProjectType': 'python2-library',
    'Md5sums': [],
    'Dependencies': [],
    'BuildDependencies': [],
    'Sources': [],
}

# FIXME: allow to pass in a static dependency resolution map
# so that this test is indendent of the system the tests runs on

if not archlinux.is_archlinux(target.get_default()):

    sys.stderr.write('WARNING: Skipping Archlinux specific tests')
else:

    class TestPkgbuildGeneration(unittest.TestCase):
        """Test PKGBUILD generation from reference input data."""

        def setUp(self):
            rec = recipe.GenericRecipe()
            rec.load(input_metadata)
            
            tar = target.Target('gnulinux-archlinux-current-i686')
            
            gen = generator.Generator()
            output = gen.generate_target_recipe(rec, tar)

            self.str = output.files()['PKGBUILD']

        def test_pkgname(self):
            self.assertEqual(pkgbuild_attribute(self.str, 'pkgname'), 'testpackage')

        def test_pkgver(self):
            self.assertEqual(pkgbuild_attribute(self.str, 'pkgver'), '0.0.1')

        def test_pkgrel(self):
            self.assertEqual(pkgbuild_attribute(self.str, 'pkgrel'), '1')

        def test_pkgdesc(self):
            self.assertEqual(pkgbuild_attribute(self.str, 'pkgdesc'), '\"This is a test package\"')

        # TODO: remove trailing whitespace after last element
        def test_pkgarch(self):
            self.assertEqual(pkgbuild_attribute(self.str, 'arch'), '(\'i686\' \'x86_64\' )')

        def test_license(self):
            self.assertEqual(pkgbuild_attribute(self.str, 'license'), '(\'GPL\' \'custom\' )')


testdata_pkgname = 'gcc-fortran-4.5.2-6'

class TestPackageNameParser(unittest.TestCase):
    
    def setUp(self):
        self.pkginfo = archlinux.arch_parse_pkgname(testdata_pkgname)

    def test_name(self):
        self.assertEqual(self.pkginfo['Name'], 'gcc-fortran')

    def test_revision(self):
        self.assertEqual(self.pkginfo['Revision'], '6')

    def test_version(self):
        self.assertEqual(self.pkginfo['Version'], '4.5.2')

testdata_files = """%FILES%
usr/
usr/include/
usr/lib/
usr/share/
usr/share/man/
usr/share/licenses/
usr/share/licenses/zlib/
usr/share/licenses/zlib/LICENSE
usr/share/man/man3/
usr/share/man/man3/zlib.3.gz
usr/lib/libz.so.1
usr/lib/pkgconfig/
usr/lib/libz.so
usr/lib/libz.so.1.2.5
usr/lib/libz.a
usr/lib/pkgconfig/zlib.pc
usr/include/zconf.h
usr/include/zlib.h"""

class TestFilesParser(unittest.TestCase):

    def setUp(self):
        self.files = archlinux.arch_parse_files(testdata_files)['Files']
    
    def test_number_of_items(self):
        self.assertEqual(len(self.files), 18)

    def test_first_item(self):
        self.assertEqual(self.files[0], 'usr/')

    def test_last_item(self):
        self.assertEqual(self.files[-1], 'usr/include/zlib.h')

testdata_depends = """%DEPENDS%
sh
tar
texinfo"""

class TestDependsParser(unittest.TestCase):

    def setUp(self):
        self.deps = archlinux.arch_parse_depends(testdata_depends)['Dependencies']
    
    def test_number_of_items(self):
        self.assertEqual(len(self.deps), 3)

    def test_first_item(self):
        self.assertEqual(self.deps[0], 'sh')

    def test_last_item(self):
        self.assertEqual(self.deps[-1], 'texinfo')

# TODO: write tests and implementation
testdata_desc = """%FILENAME%
libtool-2.4-2-x86_64.pkg.tar.xz

%NAME%
libtool

%VERSION%
2.4-2

%DESC%
A generic library support script

%GROUPS%
base-devel

%CSIZE%
386796

%ISIZE%
2297856

%MD5SUM%
10f4cbecf11f3aa43287f14551dab73c

%URL%
http://www.gnu.org/software/libtool

%LICENSE%
GPL

%ARCH%
x86_64

%BUILDDATE%
1292565262

%PACKAGER%
Allan McRae <allan@archlinux.org>"""


class TestPkglistParser(unittest.TestCase):

    repo_path = utils.get_testdata_file('core.files.tar.gz')
    _pkglist = archlinux.arch_pkglist_from_path(repo_path)

    def setUp(self):
        self.pkglist = self._pkglist
    
    def test_number_of_items(self):
        self.assertEqual(len(self.pkglist.keys()), 185)

    def test_existance(self):
        self.assertTrue('libnl-1.1-2' in self.pkglist)

    def test_name(self):
        pkg = self.pkglist['which-2.20-4']
        self.assertEqual(pkg['Name'], 'which')

    def test_version(self):
        pkg = self.pkglist['which-2.20-4']
        self.assertEqual(pkg['Version'], '2.20')

    def test_files1(self):
        pkg = self.pkglist['eventlog-0.2.12-1']
        print pkg['Files']
        self.assertEqual(len(pkg['Files']), 16)

    def test_files2(self):
        pkg = self.pkglist['glib2-2.26.1-1']
        self.assertEqual(len(pkg['Files']), 556)

        
"""
TODO: Fix implementation
    def test_dependencies(self):
        pkg = self.pkglist['which-2.20-4']
        self.assertEqual(pkg['Dependencies'], ['glibc', 'sh'])

    def test_dependencies2(self):
        pkg = self.pkglist['glib2-2.26.1-1']
        self.assertEqual(pkg['Dependencies'], ['pcre>=8.02'])
"""

if __name__ == '__main__':
    unittest.main()
