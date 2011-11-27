
"""Generator


"""

from deploymentkit.core.target import Target

import os
import os.path

def _load_backends():
    """Loads all backends from backends/ directory.
    Returns a list of GeneratorBackend classes"""

    backend_classes = []

    base_module = 'deploymentkit.backends'

    module = __import__(base_module, globals(), locals(), [])
    backends_module = module.backends

    backend_files = os.listdir(backends_module.__path__[0])
    for filename in backend_files:
        modulename = os.path.splitext(filename)[0]
        
        module = __import__(base_module + '.' + modulename, globals(), locals(), [])

        backend_module = getattr(module.backends, modulename)
        if hasattr(backend_module, "GeneratorBackend"):
            backend_class = backend_module.GeneratorBackend
            if not backend_class in backend_classes:
                backend_classes.append(backend_class)
        
    return backend_classes


class Generator(object):
    """Used to transform a GenericRecipe into a TargetRecipe."""

    _backends = _load_backends()

    @classmethod
    def supported_targets(cls):
        """Return a list of all supported targets."""

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
