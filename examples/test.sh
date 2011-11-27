#!/bin/bash

# Intended to be called like so:
# examples/test.sh gnulinux-archlinux-current-i686 all massifg
# examples/test.sh gnulinux-archlinux-current-i686 generate massifg
# examples/test.sh gnulinux-archlinux-current-i686 build massifg


### Input ###

target=$1
mode=$2
package=$3

example_dir=examples
src_dir=`pwd`

### Setup ###

# Make sure deploymentkit from source tree is found first
export PATH=$src_dir/bin:$PATH
export PYTHONPATH=$src_dir:$PYTHONPATH

# Each package should have a recipe: example_dir/package/package.yaml
output_dir=$example_dir/$package
input=$output_dir/$package.yaml

### Generate ###
dk-generate $input --output-dir=$output_dir --target $target || exit 1

### Build ###
cd $output_dir

# archlinux specific
makepkg -f --skipinteg || exit 2
