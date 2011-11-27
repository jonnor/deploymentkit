DeploymentKit - Making it easy to deploy native packages

License: LGPLv2+
Maintainer:
    Jon Nordby <jononor@gmail.com>
Dependencies:
    Python (2.7+ at the moment)
    pyyaml
    Cheetah
    Nose (optional, for running tests)

= Purpose & Scope =
Making it easier for software developers to deploy native packages,
by generating package recipes for multiple target platforms
from a single, generic package metadata format.

= Current status =
GNU/Linux-centric prototype / feasibility study

= Usage ==
# Directly from source tree
  export PYTHONPATH=./
  ./bin/dk-generate package.yaml

# Installing and using from install
  python ./setup.py install
  dk-generate package.yaml

See "dk-generate --help" and "dk-generate --help-input" for more information.

# Running tests (from source tree)
  nosetests

= Principle =
DeploymentKit defines a generic package metadata format (1),
and from this generates the target-specific package recipe (2).

The package recipe (2) and the source code (0) is then consumed
by the package builder to produce the binary distributable package
that the user can install.

                                                        0.
                                                    source code
                                                        |
   1.                                2.                 |                     3.
generic     -----------------     target-      ----------------------      Binary
package --> | DeploymentKit | --> specific --> | "PackageBuilder" * | -->  distributable
metadata    -----------------     package      ----------------------      package
                                  recipe                                   for target


* The package builder is not provided by DeploymentKit, but
shown here for completeness. A cross-target solutions like
Open Build Service (www.openbuildservice.org) can be used,
or a native toolchain for the given target.

Examples formats for some common targets/toolchains:

Target              2.                  3.
--------------------------------------------------
ArchLinux           PKGBUILD            tar.pkg.xz
Debian/Ubuntu       debian/             .deb
Fedora/openSUSE     .spec               .rpm
Windows             NSIS script         .exe/.msi

= More documentation =
See TODO.txt and the doc/ directory
