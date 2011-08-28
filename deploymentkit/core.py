
import os.path

import yaml

import deploymentkit

"""Target independent package recipe

This is similar to what the native GNU/Linux packaging systems use 
(.spec, .dsc, PKGBUILD, ebuild) but different in two significant ways:

- Metadata like dependencies, architecture, et.c. is specified in a target independent way.
- The format is designed to be easy to access programatically.

Dependencies are specified using for instance:
- pkg-config
- dbus
- executable

This target independent recipe is transformed into
a target specific recipe by DeploymentKit
"""

# TODO: formally define and document the YAML recipie format
# FIXME: some could probably be optional
generic_recipe_format = {
    # 'Attribute': ()
    # TODO: Add information about the attributes
    # Description, Type, Mandatory/Optional, Default value, Supported values
    'Name': (),
    'Version': (),
    'ReleaseVersion': (),
    'BriefDescription': (),
    'URL': (),
    'Licenses': (),
    'BuildSystemType': (),
    'Dependencies': (),
}
mandatory_attributes = generic_recipe_format.keys()

class PackageRecipe(object):
    """ """

    def __init__(self):
        self.data = {}

    def output_target_recipe(self, target_platform=None):
        """Generate the target-specific recipe.
        Returns a mapping {"filename": "content"}"""
        
        if not target_platform:
            # TODO: option to autodetect the current platform
            target_platform = deploymentkit.supported_targets['ArchLinux']

        return target_platform.generate_recipe(self)

"""Target platform

"""

# TODO: Use same platform identifiers as PackageKit? Or OBS?
supported_platforms = {}

class TargetPlatform(object):
    """Interface class for a target platform."""
    
    def __init__(self):
        pass

    def generate_recipe(self, pkg_recipe):
        """Generate a target specific package recipe from the generic @pkg_recipe
        To be implemented by a specific target platform."""
        pass


def generate_recipe(input_file, output_prefix, target_id):
	"""Generate the target-specific package recipie from
	the YAML @input_file, and write the files to the path @output_prefix."""
	
	pkg = PackageRecipe()
	pkg.data = yaml.load(open(input_file).read())

	if target_id:
	    target = deploymentkit.supported_targets[target_id]
	else:
	    target = None # Autodetect
	output_files = pkg.output_target_recipe(target)
	
	for filename, file_content in output_files.items():
		if not os.path.exists(output_prefix):
		    os.makedirs(output_prefix)
		f = open(os.path.join(output_prefix, filename), 'w')
		f.write(file_content)
		f.close()
	
