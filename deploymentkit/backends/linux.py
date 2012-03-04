
"""Common code for Linux or Linux-like systems."""

import tarfile, subprocess, os


def map_dependency(dependency_string, installed_file_to_dependency_func):
    dep = dependency_string

    if dep.startswith('pkg-config:'):
        pkgconfig_str = dep.split('pkg-config:')[1]
        pkg_name = package_from_pkgconfig(pkgconfig_str, installed_file_to_dependency_func)

    elif dep.startswith('executable:'):
        executable_name = dep.split('executable:')[1]
        pkg_name = package_from_executable(executable_name, installed_file_to_dependency_func)

    else:
        # FIXME: this detection should be done when parsing the recipe
        # TODO: support other depencency types
        raise NotImplementedError

    return pkg_name

def package_from_executable(executable_name, installed_file_to_package):
    """Return the name of the package that should be used to provide @executable_name"""

    not_installed = subprocess.check_call(['which', executable_name])
    if not_installed:
        # Naive approach:
        # Walk PATH and search in package database for package containing
        # files that matches
        #
        # Problem: some packages will add additional directories
        # to path when installed, with no way to know which ones these are
        # Only real solution here is for packages to have a provides(executable:executable-name)
        # that can be queried from the database. Should then be accesible through PackageKit
        raise NotImplementedError

    executable_path = subprocess.check_output(['which', executable_name]).strip()

    package_mapper = installed_file_to_package
    package_id = package_mapper(executable_path)

    return package_id

def package_from_pkgconfig(pkg_config_string, installed_file_to_package):
    """Return the name of package that should be used to provide @pkg_config_strig."""

    # TODO: handle version requirements
    pkg_config_id = pkg_config_string

    return package_from_pkgconfig_fallback(pkg_config_id, installed_file_to_package)


def package_from_pkgconfig_fallback(pkg_config_id, installed_file_to_package):
    # Check if package is installed
    args = ['pkg-config', '--exists', pkg_config_id]
    is_installed = not subprocess.call(args)

    if not is_installed:
        # TODO: look up in package db
        raise NotImplementedError, 'Unable to resolve non-installed dependency "%s"' % pkg_config_id

    # From man pkg-config
    # FIXME: handle lib64 correctly
    # TODO: find a more reliable way to determine the directories
    # * Get a --filename option into pkg-config, perhaps?
    # TODO: handle PKG_CONFIG_LIBDIR and PKG_CONFIG_PATH
    pkg_config_dirs = ['/usr/lib/pkgconfig',
            '/usr/share/pkgconfig',
            '/usr/local/lib/pkgconfig',
            '/usr/local/share/pkgconfig']

    # Search for the .pc file
    package_id = ''
    for dir in pkg_config_dirs:
        filepath = os.path.join(dir, pkg_config_id+'.pc')
        if os.path.exists(filepath):

            package_mapper = installed_file_to_package
            package_id = package_mapper(filepath)
            break

    assert package_id, 'Could not find .pc file, but pkg-config said it existed'

    return package_id
