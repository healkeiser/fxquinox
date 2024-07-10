class InvalidProjectError(Exception):
    """Exception raised when a project is not valid."""

    pass


class InvalidSequenceError(Exception):
    """Exception raised when a sequence is not valid."""

    pass


class InvalidSequencesDirectoryError(Exception):
    """Exception raised when a sequences directory is not valid."""

    pass


class InvalidShotError(Exception):
    """Exception raised when a shot is not valid."""

    pass


class InvalidAssetError(Exception):
    """Exception raised when an asset is not valid."""

    pass


class InvalidAssetsDirectoryError(Exception):
    """Exception raised when an assets directory is not valid."""

    pass


class InvalidStepError(Exception):
    """Exception raised when a step is not valid."""

    pass


class InvalidTaskError(Exception):
    """Exception raised when a task is not valid."""

    pass
