#!/usr/bin/env python2

import sys, os, os.path, subprocess, optparse

# Each package should have a recipe: example_dir/package/package.yaml
example_dir = 'examples'
src_dir = os.getcwd()

def prepend_path_to_env(var, value, env=os.environ):
    
    if not var in env:
        env[var] = ''
    
    env[var] = value + os.pathsep + env[var]

def build_example(example_name, target):

    # Make sure deploymentkit from source tree is found first
    env = dict(os.environ)
    prepend_path_to_env('PATH', os.path.join(src_dir, 'bin'), env)
    prepend_path_to_env('PYTHONPATH', src_dir, env)

    output_dir = os.path.join(example_dir, example_name)
    input_recipe = os.path.join(output_dir, '%s.yaml' % example_name)

    # Generate
    generate_cmd = ['dk-generate', input_recipe,
                    '--output-dir=%s' % output_dir, '--target=%s' % target]

    error_code = subprocess.call(generate_cmd, env=env)
    if error_code:
        return error_code

    # Build
    build_cmd = ['dk-build', '--target=%s' % target]
    
    error_code = subprocess.call(build_cmd, cwd=output_dir, env=env)
    if error_code:
        return error_code
        
    return 0

if __name__ == '__main__':

    parser = optparse.OptionParser(usage="Usage: %prog [options]")

    parser.add_option("-t", "--target", default='',
                      help="The targets to test.")
    parser.add_option("-e", "--examples", default="all",
                      help="The examples to test.")

    (options, args) = parser.parse_args()

    if options.examples == 'all':
        examples = os.listdir(example_dir)
        options.examples = examples
    else:
        options.examples = options.examples.split(',')

    # Build each example
    for ex in options.examples:
        error = build_example(ex, options.target)
        if error:
            sys.exit(error)
    
