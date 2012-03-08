
"""Generator


"""

from deploymentkit.core.target import Target
from deploymentkit.core import backends

import os
import os.path


class Generator(object):
    """A Generator transforms a GenericRecipe into BuildRecipes.

    Support for new targets can be added by implementing a GeneratorBackend."""

    _backends = backends.load('GeneratorBackend')

    @classmethod
    def supported_targets(cls):
        """Return a list of all supported targets."""

        # FIXME: has duplicates. Should be a set, 
        # but that requires interning of Target instances
        supported = []
        for backend in cls._backends:
            supported.extend(backend.supported_targets)
            
        return supported

    def __init__(self):
        pass

    def _find_backends(self, targets):
        return backends.find_backends_for_targets(self._backends, targets)

    def generate_build_recipes(self, generic_recipe, targets):
        """Return a list of BuildRecipes, given a GenericRecipe and a list of Targets."""

        # TODO: allow to work iteratively
        # TODO: Target-specific recipies are not only dependent on target platform
        # but also the build type and toolchain used. Add an additional parameter for this
        # DeploymentOptions ?

        def normalize_target(target):
            if not isinstance(target, Target):
                target = Target(target)
            return target

        targets = [normalize_target(t) for t in targets]

        build_recipes = []
       
        backends = self._find_backends(targets)
        for backend, targets in backends:

            # TODO: these should come as errors/warnings much earlier,
            # and be more suitable for giving proper user-feedback
            # Move into some sort of verification method, similar to
            # what exists for the recipes themselves?
            buildsystem_type = generic_recipe.data['BuildSystemType']
            if not buildsystem_type in backend.supported_buildsystems:
                raise ValueError, "BuildSystemType: \"%s\" is not supported for targets: \"%s\" with backend %s" % (buildsystem_type, targets, backend)
            if not backend:
                raise ValueError, "targets: %s are not supported" % targets


            backend_instance = backend()
            build_recipe = backend_instance.generate_build_recipe(generic_recipe, targets)        
            build_recipes.append(build_recipe)
        
        return build_recipes


class GeneratorBackendInterface(object):
    """Interface for Generator backends."""
    
    supported_targets = [] # List of Target instances
    supported_buildsystems = [] # List of strings
    
    def __init__(self):
        pass
        
    
    def generate_build_recipe(self, generic_recipe, targets):
        pass
