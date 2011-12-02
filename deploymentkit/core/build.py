"""Building a DeploymentKit or target-specific recipe."""

class Builder(object):

	@staticmethod
	def supported_targets():
		from deploymentkit.backends import archlinux
		return archlinux.GeneratorBackend.supported_targets

	def __init__(self):
		self._target = None

	def run(self):

		from deploymentkit.backends import archlinux
		# FIXME: generic way of doing this

		return archlinux.build(self._target)

	def get_target(self, target):
		return self._target

	def set_target(self, target):
		self._target = target

	target = property(get_target, set_target)
