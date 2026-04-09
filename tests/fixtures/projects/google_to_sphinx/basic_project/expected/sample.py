"""Sample module with Google-style docstrings."""


def greet(name: str, loud: bool = False) -> str:
    """Generate a greeting message.

    :param name: The name to greet.
    :type name: str
    :param loud: Whether to use uppercase. Defaults to False.
    :type loud: bool
    :returns: The greeting message.
    :rtype: str
    :raises ValueError: If name is empty.
    """
    if not name:
        raise ValueError("Name cannot be empty")
    msg = f"Hello, {name}!"
    return msg.upper() if loud else msg


class Greeter:
    """A class that greets people.

    :param prefix: Greeting prefix. Defaults to "Hello".
    :type prefix: str
    """

    def __init__(self, prefix: str = "Hello") -> None:
        """Initialize the Greeter.

        :param prefix: The greeting prefix.
        :type prefix: str
        """
        self.prefix = prefix

    def greet(self, name: str) -> str:
        """Greet someone.

        :param name: Person to greet.
        :type name: str
        :returns: The greeting.
        :rtype: str
        """
        return f"{self.prefix}, {name}!"

    async def greet_async(self, name: str) -> str:
        """Greet someone asynchronously.

        :param name: Person to greet.
        :type name: str
        :returns: The greeting.
        :rtype: str
        """
        return f"{self.prefix}, {name}!"
