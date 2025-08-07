import random
import string
from typing import Dict, Generic, Iterable, Protocol, TypeVar

K = TypeVar("K")


class Expirable(Protocol):
    """Protocol for objects that can expire."""

    def is_expired(self) -> bool:
        """Return True if the object has expired, False otherwise."""
        ...


V = TypeVar("V", bound=Expirable)


class PrunableDict(Generic[K, V]):
    """A dictionary that prunes itself when items expire."""

    def __init__(self):
        """Initialize an empty PrunableDict."""
        self._data: Dict[K, V] = {}

    def __getitem__(self, key: K) -> V:
        """Get an item by key, raising KeyError if not found."""
        return self._data[key]

    def __setitem__(self, key: K, value: V) -> None:
        """Set an item by key, replacing it if it already exists."""
        self._data[key] = value

    def __delitem__(self, key: K) -> None:
        """Delete an item by key."""
        del self._data[key]

    def __contains__(self, key: K) -> bool:
        """Check if the key exists in the dictionary."""
        return key in self._data

    def __len__(self) -> int:
        """Return the number of items in the dictionary."""
        return len(self._data)

    def get(self, key: K, default: V = None) -> V:
        """Get an item by key, returning default if not found."""
        return self._data.get(key, default)

    def items(self) -> Iterable[tuple[K, V]]:
        """Return an iterable of key-value pairs."""
        return self._data.items()

    def prune(self) -> None:
        """Remove items that have expired."""
        working_data = self._data.copy()  # Copy to avoid modifying while iterating

        keys_to_remove = [key for key, value in working_data.items() if value.is_expired()]
        for key in keys_to_remove:
            del working_data[key]

        self._data = working_data


def random_string(length: int) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for _ in range(length))
