"""deploymentkit.distutils_integration.recipe

Implements the DeploymentKit 'recipe' command for DistUtils.
"""

__revision__ = "1"

from distutils.core import Command


def metadata_from_distribution(distribution):
    """Return a metadata object from the Distutils @distribution."""

class recipe(Command):
    description = "Create package recipies using DeploymentKit"

    user_options = [ # long name, short name, help
        ('', '', ""),
    ]
    user_options = []

    def initialize_options (self):
        self.x = None

    def finalize_options (self):
        if self.x is None:
            self.x = None

    def run (self):
        print "ran setup.py recipe"
