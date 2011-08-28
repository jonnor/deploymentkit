import unittest, os

from deploymentkit import linux, archlinux, core

pkgbuild_attribute = archlinux.pkgbuild_attribute

# FIXME: make lookup independent of current working directory
def get_testdata_file(basename):
    path = os.path.join('tests/data', basename)
    return path

class TestParsePkgbuild(unittest.TestCase):
    
    def setUp(self):
        self.file = open(get_testdata_file('PKGBUILD'))
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
    'BuildSystemType': 'autotools',
    'Dependencies': [],
    'BuildDependencies': [],
    'Sources': [],
}

class TestPkgbuildGeneration(unittest.TestCase):

    def setUp(self):
        pkg = core.PackageRecipe()

        pkg.data = input_metadata
        target = linux.Linux('ArchLinux')
        output = target.generate_recipe(pkg)

        self.str = output['PKGBUILD']

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

if __name__ == '__main__':
    unittest.main()
