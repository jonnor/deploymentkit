import unittest, os

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
    'BuildSystemType': 'autotools',
    'Dependencies': [],
    'BuildDependencies': [],
    'Sources': [],
}

class TestPkgbuildGeneration(unittest.TestCase):
    """Test PKGBUILD generation from reference input data."""

    def setUp(self):
        rec = recipe.PackageRecipe()
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

if __name__ == '__main__':
    unittest.main()