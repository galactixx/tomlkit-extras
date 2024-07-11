class BaseError(Exception):
    """Base error class."""
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return self.message
    

class TOMLDecodingError(BaseError):
    """Decoding error occurring when loading a TOML configuration file."""
    def __init__(self, message: str):
        super().__init__(message=message)


class TOMLConversionError(BaseError):
    """General TOML conversion error."""
    def __init__(self, message: str):
        super().__init__(message=message)