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
        self._target = None

    def run(self):

        backend = self._find_backend()()

        return backend.run(self._target)

    def get_target(self, target):
        return self._target

    def set_target(self, target):
        self._target = target

    target = property(get_target, set_target)

    def _find_backend(self):
        """Return the appropriate backend to use."""

        target = self._target

        found_backend = None

        for backend in self._backends:

            if target in backend.supported_targets:
                if found_backend:
                    print "Warning: Multiple backends supporting target: %s found" % target
                    # TODO: better logging

                else:
                    found_backend = backend

        return found_backend

class BuilderBackendInterface(object):

    supported_targets = []

    def __init__(self):
        pass

    def run(self, target):
        pass
