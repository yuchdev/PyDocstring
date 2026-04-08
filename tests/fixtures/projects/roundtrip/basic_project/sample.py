"""Roundtrip fixture: Google style source for roundtrip testing."""


def process(items: list, key: str = "id") -> dict:
    """Process a list of items.

    Args:
        items (list): The items to process.
        key (str): The key to use. Defaults to "id".

    Returns:
        dict: Processed result mapping.

    Raises:
        KeyError: If key not found in any item.
        ValueError: If items is empty.

    Examples:
        >>> process([{"id": 1}])
        {"1": {"id": 1}}
    """
    if not items:
        raise ValueError("items cannot be empty")
    return {str(item[key]): item for item in items}
