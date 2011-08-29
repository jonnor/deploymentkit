DeploymentKit - Making it easy to deploy native packages

License: LGPLv2+
Maintainer:
    Jon Nordby <jononor@gmail.com>
Dependencies: 
    Python (2.7+ at the moment)
    pyyaml
    Cheetah

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
dk-generate

Pass the --help flag for more information.

= Principle =
                                                        0.
                                                    source code
                                                        |
   1.                                2.                 |                     3.
generic     -----------------     target-      ----------------------      Binary
package --> | DeploymentKit | --> specific --> | "PackageBuilder" * | -->  distributable
metadata    -----------------     package      ----------------------      package
                                  recipe                                   for target

DeploymentKit defines a generic package metadata format (1),
and from this generates the target-specific package recipe (2).

The package recipe (2) and the source code (0) is then consumed 
by the package builder to produce the binary distributable package
that the user can install.

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

= TODO =
See also the numerous FIXME, TODO and XXX comments in the source code.

== 0.1.0 release ==
Criteria:
    Can build simple package recipes for common GNU/Linux targets
        Ubuntu/Fedora/ArchLinux
    Name has been decided?

== In DeploymentKit ==
* Extend existing target support
 * Resolve non-installed dependencies
 * Multiple (sub/binary) packages
 * Post/Pre Install/Uninstall script support

* New build system support
 * qmake
 * python distutils
 * cmake
 * scons

* New target support
 * Fedora
 * RHEL/CentOS
 * Debian
 * Ubuntu
 * Mandriva
 * Gentoo
 * other GNU/Linux...
 
 * Windows mingw32 (MSI/NSIS)
 * Mac OSX (macports/fink/dmg/app bundle)

 * BSDs et.c.

* Support for packages bundling for GNU/Linux targets

* Testing
 * Set up CI system with integration tests

== In related projects ==
PackageKit:
    * Method of querying package for executables
    * Method of querying package for pkg-config identifiers
    
Open Build Service:
    * Arch Linux support (2011 OpenSUSE GSOC)
    * Support for running DeploymentKit 
    to generate the target recipes
