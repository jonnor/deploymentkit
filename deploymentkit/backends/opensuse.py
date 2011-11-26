
from deploymentkit.core import recipe, target

class OpensuseTargetRecipe(recipe.TargetRecipe):
    
    def files(self):
        return self._files

class GeneratorBackend(object):

    supported_targets = [
        target.Target("gnulinux-opensuse-12.1-x86_64"),
        target.Target("gnulinux-opensuse-12.1-i686"),
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
        
        output = OpensuseTargetRecipe()
        output._files = files
        
        return output


def generic_to_specific_recipe(generic_data):
    """Return a mapping representing the target specific recipe data
    based on the @generic_data"""

    # XXX: perhaps the generic and target-specific data
    # should be made available to the template engine as two
    # different instances?
    specific_data = {}
    specific_data.update(generic_data)

    build_commands = ['%configure --disable-static', 'make %{?jobs:-j%jobs}']
    install_commands = ['%makeinstall', 'find %{buildroot} -type f -name "*.la" -delete -print']

    specific_data['BuildCommands'] = build_commands
    specific_data['InstallCommands'] = install_commands

    # Resolve dependencies to native packages
    specific_data['Dependencies'] = []
    for dep in generic_data['Dependencies']:
        specific_data['Dependencies'].append(map_dependency(target, dep))

    specific_data['BuildDependencies'] = []
    for dep in generic_data['BuildDependencies']:
        specific_data['BuildDependencies'].append(map_dependency(target, dep))

    specific_data['PrepCommands'] = ['%setup -q']
    specific_data['CleanCommands'] = ['rm -rf %{buildroot}']

    specific_data['Files'] = """%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/*"""

    # TODO: only if the package is of type=library or similar
    update_ldconfig = '-p /sbin/ldconfig'
    specific_data['PostUninstall'] = update_ldconfig
    specific_data['PostInstall'] = update_ldconfig

    return specific_data
