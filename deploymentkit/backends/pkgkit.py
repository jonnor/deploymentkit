"""Common backend code for PackageKit"""

import subprocess

def package_from_pkgconfig_packagekit(target, pkg_config_id):

    pkg_config_file = pkg_config_id + '.pc'
    pkg_name = package_from_file_packagekit_subprocess(pkg_config_file)
    return pkg_name

def package_from_file_packagekit_python(filepath):
    # As of 28.08.2011 on Arch Linux the search_file query fails
    # with unable to find dbus method SearchFiles with signature (ss)

    import packagekit.client
    pk_client = packagekit.client.PackageKitClient()
    packages = pk_client.search_file(filepath)

def package_from_file_packagekit_subprocess(filepath):
    output = subprocess.check_output(['pkcon', 'search', 'file', filepath])
    # Output is on the form
    #Transaction:   Searching by name
    #Status:    Querying
    #Package:   gegl-0.1.6-1.x86_64
    #Package:   gegl-gtk-git-20110721-1.x86_64
    #Results:
    #Installed    gegl-0.1.6-1.x86_64
    #Installed    gegl-gtk-git-20110721-1.x86_64

    packages = []
    installed_packages = []
    for line in output.split("\n"):
        if line.startswith('Package:'):
            pkg_id = line.split('Package:')[1].strip()
            packages.append(pkg_id)
        if line.startswith('Installed'):
            pkg_id = line.split('Installed')[1].strip()
            installed_packages.append(pkg_id)

    if len(packages) == 0:
        return ''
    elif len(packages) == 1:
        pkg_id = packages[0]
    else:
        # XXX: Can we handle mutiple packages providing the same file better?
        # FIXME: handle architecture differences correctly
        # TODO: use logging module instead
        print "Warning: Multiple package matches found for pkgconfig identifier %s" % pkg_config_id
        pkg_id = packages[0]


    # Target specific
    # Arch Linux specific?
    # Strip away architecture
    # gegl-gtk-git-20110721-1.x86_64 -> gegl-gtk-git-20110721-1
    pkg = pkg_id[0:pkg_id.rindex('.')]

    # Strip away version number
    # Packages are on format:
    # $pkgname-$version-$build_revision
    # where only $pkgname can contain dashes
    # gegl-gtk-git-20110721-1 -> gegl-gtk-git
    pkg_name = '-'.join(pkg.split('-')[0:-2])

    return pkg_name
