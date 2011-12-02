
"""Generator


"""

from deploymentkit.core.target import Target
from deploymentkit.core import backends

import os
import os.path


class Generator(object):
    """Used to transform a GenericRecipe into a TargetRecipe."""

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

    def _find_backend(self, target):
        """Return the appropriate GeneratorBackend to use for @target"""

        found_backend = None
        
        for backend in self._backends:

            if target in backend.supported_targets:
                if found_backend:
                    print "Warning: Multiple backends supporting target: %s found" % target
                    # TODO: better logging
                    
                else:
                    found_backend = backend
                    
        return found_backend

    def generate_target_recipe(self, generic_recipe, target):
        """Return a TargetRecipe, given a GenericRecipe and a Target."""

        # TODO: allow to work iteratively
        # TODO: Target-specific recipies are not only dependent on target platform
        # but also the build type and toolchain used. Add an additional parameter for this
        # DeploymentOptions ?
        
        if not isinstance(target, Target):
            target = Target(target)
        
        backend = self._find_backend(target)
        
        if not backend:
            raise ValueError, "target: %s is not supported" % target

        buildsystem_type = generic_recipe.data['BuildSystemType']
        if not buildsystem_type in backend.supported_buildsystems:
            raise ValueError, "BuildSystemType: \"%s\" is not supported for target: \"%s\" with backend %s" % (buildsystem_type, target, backend)

        backend_instance = backend()
        target_recipe = backend_instance.generate_target_recipe(generic_recipe, target)
        
        return target_recipe


class GeneratorBackendInterface(object):
    """Interface for Generator backends."""
    
    supported_targets = [] # List of Target instances
    supported_buildsystems = [] # List of strings
    
    def __init__(self):
        pass
        
    
    def generate_target_recipe(self, generic_recipe, target):
        pass
