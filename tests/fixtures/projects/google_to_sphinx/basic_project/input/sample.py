"""Sample module with Google-style docstrings."""


def greet(name: str, loud: bool = False) -> str:
    """Generate a greeting message.

    Args:
        name (str): The name to greet.
        loud (bool): Whether to use uppercase. Defaults to False.

    Returns:
        str: The greeting message.

    Raises:
        ValueError: If name is empty.
    """
    if not name:
        raise ValueError("Name cannot be empty")
    msg = f"Hello, {name}!"
    return msg.upper() if loud else msg


class Greeter:
    """A class that greets people.

    Args:
        prefix (str): Greeting prefix. Defaults to "Hello".
    """

    def __init__(self, prefix: str = "Hello") -> None:
        """Initialize the Greeter.

        Args:
            prefix (str): The greeting prefix.
        """
        self.prefix = prefix

    def greet(self, name: str) -> str:
        """Greet someone.

        Args:
            name (str): Person to greet.

        Returns:
            str: The greeting.
        """
        return f"{self.prefix}, {name}!"

    async def greet_async(self, name: str) -> str:
        """Greet someone asynchronously.

        Args:
            name (str): Person to greet.

        Returns:
            str: The greeting.
        """
        return f"{self.prefix}, {name}!"
