
import tarfile, subprocess, os

from Cheetah.Template import Template
import yaml

from deploymentkit.core import recipe, target
from deploymentkit.backends import linux

class ArchLinuxTargetRecipe(recipe.TargetRecipe):
    
    def files(self):
        return self._files

class GeneratorBackend(object):

    supported_targets = [
        target.Target("gnulinux-archlinux-current-x86_64"),
        target.Target("gnulinux-archlinux-current-i686"),
    ]
    
    supported_buildsystems = [
        'autotools',
    ]

    def __init__(self):
        pass
        
    def generate_target_recipe(self, generic_recipe, target):
    
        assert target in self.supported_targets
    
        # Map target independent values into target specific values.
        target_pkg_recipe = generic_to_specific_recipe(generic_recipe.data)

        # Create the target specific recipe
        try:
            files = generate_recipe(target_pkg_recipe)
        except KeyError:
            files = {}
        
        output = ArchLinuxTargetRecipe()
        output._files = files
        
        return output

def generic_to_specific_recipe(generic_data):
    """Return a mapping representing the target specific recipe data
    based on the @generic_data"""

    # XXX: perhaps the generic and target-specific data
    # should be made available to the template engine as two
    # different instances?
    # YES, or more
    # recipe.InputAttribute
    # linux.LinuxSpecificAttribute
    # archlinux.ArchLinuxSpecificAttribute
    
    specific_data = {}
    specific_data.update(generic_data)

    build_commands = ['./configure --prefix=/usr', 'make']
    install_commands = ['make DESTDIR="$pkgdir" install']

    specific_data['BuildCommands'] = build_commands
    specific_data['InstallCommands'] = install_commands

    # Resolve dependencies to native packages
    specific_data['Dependencies'] = []
    for dep in generic_data['Dependencies']:
        specific_data['Dependencies'].append(linux.map_dependency(dep, map_installed_file_to_package))

    specific_data['BuildDependencies'] = []
    for dep in generic_data['BuildDependencies']:
        specific_data['BuildDependencies'].append(linux.map_dependency(dep, map_installed_file_to_package))


    specific_data['SupportedArchitectures'] = ['i686', 'x86_64']

    return specific_data
    

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
