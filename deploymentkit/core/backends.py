
import os
import os.path

def load(backend_type):
    """Loads all backends from backends/ directory.
    Returns a list of backend classes of the given @backend_type.
    backend_type is expected to be a string representing the
    clasname for the backend."""

    backend_classes = []

    base_module = 'deploymentkit.backends'

    module = __import__(base_module, globals(), locals(), [])
    backends_module = module.backends

    backend_files = os.listdir(backends_module.__path__[0])
    for filename in backend_files:
        modulename = os.path.splitext(filename)[0]
        
        module = __import__(base_module + '.' + modulename, globals(), locals(), [])

        backend_module = getattr(backends_module, modulename)
        if hasattr(backend_module, backend_type):
            backend_class = getattr(backend_module, backend_type)
            if not backend_class in backend_classes:
                backend_classes.append(backend_class)
        
    return backend_classes

def find_backend_for_target(backends, target):
    found_backend = None
    
    for backend in backends:

        if target in backend.supported_targets:
            if found_backend:
                print "Warning: Multiple backends supporting target: %s found" % target
                # TODO: better logging
                
            else:
                found_backend = backend

    if not found_backend:
        print "Warning: No backend found for target: %s" % target

    return found_backend
