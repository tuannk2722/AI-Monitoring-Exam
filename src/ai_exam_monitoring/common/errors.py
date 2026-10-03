class ProjectError(Exception):
    """Base error for actionable project failures."""


class ConfigurationError(ProjectError):
    """Configuration is missing, invalid or unsafe to execute."""


class DataContractError(ProjectError):
    """Dataset input violates a canonical contract."""


class PhaseNotReadyError(ProjectError):
    """A later-phase capability was invoked before its entry gate was met."""
