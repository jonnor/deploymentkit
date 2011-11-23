"""Target platform

"""

# FIXME: Target-specific recipies are not only dependent on platform
# but also the build type and toolchain used.
# FIXME: Require target backends to specify supported targets and the build types

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
        pkg.load_from_string(open(input_file).read())

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
