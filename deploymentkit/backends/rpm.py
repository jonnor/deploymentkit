
"""Common code for RPM-based targets."""

import subprocess

from Cheetah.Template import Template

def generate_recipe(metadata):

    pkg_name = metadata['Name']

    return {pkg_name + '.spec': create_spec(metadata)}

def map_installed_file_to_package(filename):
    output = subprocess.check_output(['rpm', '-qf', filename])
    # Output is on form:
    # glib2-devel-2.28.0-3.6.1.i586
    pkg_id = output
    pkg = pkg_id[0:pkg_id.rindex('.')]
    pkg_name = '-'.join(pkg.split('-')[0:-2])
    return pkg_name

def create_spec(metadata):
    """Return a string representing a spec file generated from @metadata"""

    # FIXME: don't hardcode
    template_path = 'data/spec.tmpl'

    template_definition = open(template_path).read()

    spec_str = str(Template(template_definition, searchList=metadata))

    return spec_str
