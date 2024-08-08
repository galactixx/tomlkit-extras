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


class InvalidHierarchyError(BaseError):
    """Error occurring when a hierarchy does not exist in set of expected hierarchies."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidFieldError(BaseError):
    """Error occurring when a field does not exist in set of expected fields."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidTableError(BaseError):
    """Error occurring when a table does not exist in set of expected table."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidArrayOfTablesError(BaseError):
    """Error occurring when referencing an invalid array of tables."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidStylingError(BaseError):
    """Error occurring when a styling does not exist in set of expected stylings."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidArrayItemError(BaseError):
    """Error occurring when an item expected to exist in an array, does not."""
    def __init__(self, message: str):
        super().__init__(message=message)