"""Generate data files with distribution information.
From distribution specific format/source to distribution independent format."""

# Output format
# - package-list
# Name, Version, Revision
# - package-info
# Files, et.c.
# 
# Internal format
# Just mappings representing output format

# Arch Linux repo info can be done using the files that pkgtools/pkgfile maintains
# Syncing: pkgfile -s
# Format:
# /var/cache/pkgtools/lists/
#   repositoryname.files.tar.gz
#       packagename-version-revision/
#           desc: package metadata
#           files: list of files
#           depends: runtime dependencies

import tarfile, tempfile
import os.path

import yaml

# TODO:
# Make object oriented
#
# class Distribution(object)
# """Contains all the information about a distibution, and provides method to query."""
#
# class DistributionInfoLoader(object):
# """Responsible for loading information into a Distribution object.
# Will often have distribution-specific implementations."""
# Load from file, dynamically query
#
# ?
# Save to file (common file format)
#
#
# resolve_dependency()
# architecture() ?



def file_package_map_from_repoinfo(repo_info):
    """Return a mapping between files and packages.
    Packages are ordered in preferred order."""
    # TODO: implement
    # Challenge: the preferred order depends on the configuration of the system
    # for instance, the order of repositories

    info = {
        'path/1': ['package1'],
        'path/2': ['package2'],
    }

    return info

def package_from_pkgconfig(file_package_map, pkg_config_id):
    """Return the name of package that should be used to provide @pkg_config_id."""
    return ''

# TODO: Move to scripts.py, have a executable wrapper
# Use optparse for some sensible options and error handling
if __name__ == '__main__':

