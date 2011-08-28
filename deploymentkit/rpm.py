
"""Common code for RPM-based targets."""

def generate_recipe(metadata):

    pkg_name = metadata['Name']
    # TODO: implement
    return {pkg_name + '.spec': ''}

def map_installed_file_to_package(filename):
    raise NotImplementedError
    
    return package_id
