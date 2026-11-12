"""Adapters: the only place where knowledge of a Source lives."""


class UnreadableFile(Exception):
    """A file that cannot be turned into a Log. The message names the cause."""
