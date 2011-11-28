
from deploymentkit.core import backends


class PlatformInfoBackendInterface(object):
    
    def __init__(self):
        pass
        
    def extract(self, target, output_dir):
        pass

class PlatformInfo(object):
    
    _backends = None
    
    def __init__(self):
        self._target = None
        
    def set_target(self, target):
        self._target = target
        
    def get_target(self):
        return self._target
        
    target = property(get_target, set_target)

    def extract(self, output_dir):
        backend = self._find_backend(self.target)()
        backend.extract(self.target, output_dir)
        
    def _find_backend(self, target):
        if not self._backends:
            self._backends = backends.load('PlatformInfoBackend')
                    
        return backends.find_backend_for_target(self._backends, target)
