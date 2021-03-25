class Error(Exception):
    """Base class for other exceptions"""
    pass

class NoImagesError(Error):
    """Raised when the search query returns no images.
    
    Attributes:
        message -- explanation of the error
    """
    
    def __init__(self, message="Unable to find an image based on that phrase. Please try something else."):
        self.message = message
        super().__init__(self.message)
        
        
class DisplayTimingError(Error):
    """Raised when the display has recently been changed.
    
    Attributes:
        message -- explanation of the error
        time_remaining -- time till display can be changed again
    """
    
    def __init__(self, time_remaining, message="Display was recently changed. Please try again soon."):
        self.message = message
        self.time_remaining = time_remaining
        super().__init__(self.message)