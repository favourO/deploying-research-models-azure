"""Minimal storage port for later local and Azure Blob adapters."""

from typing import Protocol


class ObjectStorage(Protocol):
    def read(self, key: str) -> bytes:
        """Read an object by key."""
        ...

    def write(self, key: str, content: bytes) -> None:
        """Write an object by key."""
        ...
