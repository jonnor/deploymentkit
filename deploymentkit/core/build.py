"""Building a DeploymentKit or target-specific recipe."""

from deploymentkit.core import backends

class Builder(object):

    _backends = backends.load('BuilderBackend')

    @classmethod
    def supported_targets(cls):

        supported = []
        for backend in cls._backends:
            supported.extend(backend.supported_targets)

        return supported

    def __init__(self):
        pass

    def run(self, recipe, targets_restriction):
        targets_to_build = set(recipe.targets).intersection(set(targets_restriction))
        
        if targets_to_build:
            backend = self._find_backend(recipe)()
            return backend.run(recipe, targets_to_build)
        else:
            return None

    def _find_backend(self, recipe):
        """Return the appropriate backend to use."""

        return backends.find_build_backend_for_toolchain(self._backends, recipe.toolchain)

class BuilderBackendInterface(object):

    supported_targets = []
    toolchain = ''

    def __init__(self):
        pass

    def run(self, build_recipe, targets):
        """Should return True on success, false on failure"""
        # FIXME: allow to return a richer status object, with success/failure and detail
        # FIXME: make this iterable, so that the consumer can drive each iteration over targets
        pass
