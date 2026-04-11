"""Domain-specific exceptions for the game client."""


class LegendError(Exception):
    """Base exception for all labyrinth errors."""
    pass


class CharactersError(LegendError):
    """Base error for the GroupDynamics container."""
    pass


class UnknownCharacterError(CharactersError):
    """Raised when a character (by name/alias) is not found in the registry."""
    pass


class DuplicateAliasError(CharactersError):
    """Raised when attempting to register an alias that already resolves elsewhere."""
    pass


class NotFoundError(LegendError):
    """Raised when a requested resource (node, graph, etc.) is not found."""
    pass


class InvalidChoiceError(LegendError):
    """Raised when an invalid choice index is provided."""
    pass


class GraphInvariantError(LegendError):
    """Raised when a graph structure violates expected invariants."""
    pass


class ConfigurationError(LegendError):
    """Raised when there's a configuration problem."""
    pass


class ValidationError(LegendError):
    """Raised when validation fails."""
    pass
