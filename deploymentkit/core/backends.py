
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



def find_backends_for_targets(all_backends, targets):

    def overlapping_target_support(all_backends):
        # Return True if two or more backends support the same target, else False
        for this_backend in all_backends:
            for other_backend in all_backends:
                if this_backend is other_backend:
                    continue
                
                this = set(this_backend.supported_targets)
                other = set(other_backend.supported_targets)
                if this.intersection(other):
                    return True
                    
        return False

    def nestify_backend_list(input):
        # Map from [ (backend1, target1), (backend1, target2), ... ] to
        # [ (backend1, (target1, target2), ... ]
        output = []
        unique_backends = set([b for b, t in input])
    
        for backend in unique_backends:
            targets = [t for b, t in backends_for_targets if b == backend]
            output.append((backend, targets))
        return output

    assert not overlapping_target_support(all_backends)
    # Note: Right now the sets of supported targets for
    # the different backends are not intersecting
    # In the future this will likely change, as there
    # are many ways of deploying for a given target
    # We will then have to resort to a more complicated resolution
    # of backends, with defaults and ways to override these defaults
    
    # PERFORMANCE: High complexity here, can very likely be improved
    backends_for_targets = [(find_backend_for_target(all_backends, t), t) for t in targets]   
    backends_for_targets = nestify_backend_list(backends_for_targets)
    
    return backends_for_targets

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

def find_build_backend_for_toolchain(all_backends, toolchain):
    found_backend = None
    
    for backend in all_backends:
        if backend.toolchain == toolchain:
            if found_backend:
                print 'Warning: Multiple backends found for toolchain: %s' % toolchain
            else:
                found_backend = backend
    
    if not found_backend:
        print 'Warning: No backend found for toolchain: %s' % toolchain
        
    return found_backend
