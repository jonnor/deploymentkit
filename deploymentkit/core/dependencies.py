
"""Resolving dependencies


* Dynamic resolving
Dependencies are resolved dynamically at recipe generation time by
querying the target system. Only possible when DK is running on the target
system.

* Static resolving
Dependencies are resolved using a pre-created "static" dependency map.
More general solution, as the dependency maps for targets can be made
available on-line through web APIs, or as simple file downloads.

Notes:
- Dynamic resolving also creates a dependency map. This can be used later
for static resolving, either as a cache for a given recipe, or as a complete
static dependency map for the given target.

- One should be able to override the standard dep resolution manually,
in case of wrong information provided by the resolver.
"""

class DependencyResolver(object):

	def __init__(self):
		pass

	def resolve(self, dependency_string):
		"""Return the native dependency from the generic dependency specifier."""
		pass

class DependencyMap(object):
	""" 
	Mapping between	DK generic dependency specifiers and
	target dependency specifiers.

	Ideally the mapping would be many-to-one for a given target,
	but in practice this might not always be the case. One generic dependency
	might have several target dependencies that could satisfy it.

	mapping = {
		'ArchLinux': {
			'pkgconfig:gegl': ['gegl'],
			'executable:gegl': ['gegl'],
		}

		'openSUSE': {
			
		}

		}

	"""	
	
	# PERFORMANCE: This datastructure is designed for consumption by the dependency resolver.

	def __init__(self):
		self._mapping = {}
	
	

class DependencyMapBuilder(object):
	"""Build a dependency map.

	"""

	# PERFORMANCE: Building a complete map for a target dynamically, would
	# likely benefit from using an intermediate data structure where several
	# workers can add entries with minimal or no syncronization.
	# A single worker can then convert this to the required output format.

	def __init__(self):
		pass





