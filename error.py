class Error(Exception):
    """Base class for other exceptions"""
    pass

class NoImagesError(Error):
    """Raised when the search query returns no images"""
    pass