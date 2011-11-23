
import tarfile, subprocess, os

from Cheetah.Template import Template
import yaml


def generate_recipe(metadata):
    # FIXME: support package.install files
    # for {pre,post}{install,uninstall} targets
    
    pkgbuild = create_pkgbuild(metadata)
    return {'PKGBUILD': pkgbuild}

def map_installed_file_to_package(filename):
    output = subprocess.check_output(['pacman', '-Qo', filename])
    # Output is on form: "/usr/lib/pkgconfig/sm.pc is owned by libsm 1.2.0-1"
    package_id = output.split()[-2]
    
    return package_id

def create_pkgbuild(metadata):
    """Return a string representing a PKGBUILD generated from @metadata"""
    
    # FIXME: don't hardcode
    template_path = 'data/PKGBUILD.tmpl'

    template_definition = open(template_path).read()

    pkgbuild_str = str(Template(template_definition, searchList=metadata))

    return pkgbuild_str

# For testing
def pkgbuild_attribute(pkgbuild, attribute):
    """Return the value of a given @attribute in @pkgbuild.
    The entire value string is returned, or empty string if the attribute is not found.
    NB: Not anywhere close to a decent PKGBUILD parser, only designed to work on
    well-known, super-well-formed input. Used for testing out PKGBUILD generator.
    """

    value = ''

    def parse_attribute_value(line, attribute_name):
        if line.startswith(attribute_name+'='):
            k, v = line.split('=')
            return v

    for line in pkgbuild.split('\n'):
        val = parse_attribute_value(line, attribute)
        if val:
            if value:
                raise ValueError, 'attribute occured twice in PKGBUILD'
            value = val

    return value
