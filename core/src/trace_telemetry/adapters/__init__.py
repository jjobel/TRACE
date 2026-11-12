"""Adapters: the only place where knowledge of a Source lives."""


class UnreadableFile(Exception):
    """A file that cannot be turned into a Log.

    Both parts are sentences shown to the user: `cause` says what is wrong
    with the file, `remedy` what they can do about it.
    """

    def __init__(self, cause: str, remedy: str) -> None:
        super().__init__(cause)
        self.cause = cause
        self.remedy = remedy
