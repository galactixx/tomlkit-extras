import os
from pathlib import Path
from typing import (
    Any,
    Dict,
    Optional,
    Union
)

import tomlkit
from tomlkit import TOMLDocument
from tomlkit.exceptions import ParseError
import charset_normalizer
from charset_normalizer import CharsetMatch
from pathvalidate import (
    validate_filepath, 
    ValidationError
)

from tomlkit_extras._utils import from_dict_to_toml_document
from tomlkit_extras._exceptions import (
    TOMLConversionError,
    TOMLDecodingError
)

def _read_toml(toml_content: str) -> TOMLDocument:
    """
    A private function which converts an instance of a string, that being
    a string representation of a TOML file, into a tomlkit.TOMLDocument
    instance.
    """
    try:
        toml_content_parsed: TOMLDocument = tomlkit.parse(toml_content)
        return toml_content_parsed
    except ParseError as e:
        raise TOMLDecodingError("Issue occured when decoding the TOML source content")
    except Exception:
        raise TOMLConversionError(
            "Unexpected issue occured when loading the source from TOML"
        )


def _load_toml(toml_content: Union[str, bytes]) -> TOMLDocument:
    """
    A private function which accepts either a string or bytes instance, 
    being a string or bytes representation of a TOML file respectively, into
    a tomlkit.TOMLDocument instance.
    """
    if isinstance(toml_content, bytes):
        detected_encoding: Optional[CharsetMatch] = (
            charset_normalizer.from_bytes(toml_content).best()
        )
        
        # Default to utf-8 encoding if encoding was not detected
        toml_encoding: str = 'utf-8'

        if detected_encoding is not None:
            toml_encoding = detected_encoding.encoding

        # Decode content and parse into dictionary
        toml_content_decoded: str = toml_content.decode(toml_encoding)
        return _read_toml(toml_content=toml_content_decoded)
    else:
        return _read_toml(toml_content=toml_content)


def load_toml_file(
    toml_source: Union[str, bytes, bytearray, Path, TOMLDocument, Dict[str, Any]]
) -> TOMLDocument:
    """
    Accepts a string, bytes, bytearray, Path, tomlkit.TOMLDocument, or
    Dict[str, Any] instance and converts it into a tomlkit.TOMLDocument
    instance.
    
    Args:
        toml_source (str | bytes | bytearray | Path | TOMLDocument | Dict[str, Any]):
            A string, bytes, bytearray, Path, tomlkit.TOMLDocument, or Dict[str, Any]
            instance.
    
    Returns:
        tomlkit.TOMLDocument: A tomlkit.TOMLDocument instance.    
    """    
    if isinstance(toml_source, (str, Path)):
        if os.path.isfile(toml_source):
            with open(toml_source, mode="rb") as file:
                toml_content = file.read()

            return _load_toml(toml_content=toml_content)
        
        try:
            toml_source_as_path = Path(toml_source)
            validate_filepath(file_path=toml_source_as_path)
        except ValidationError:
            pass
        else:
            raise FileNotFoundError(
                "If path is passed in as the source, it must link to an existing file"
            )

        if isinstance(toml_source, str):
            return _load_toml(toml_content=toml_source)
        else:
            raise TOMLConversionError(
                "Unexpected issue occured when loading the source from TOML"
            )
    elif isinstance(toml_source, TOMLDocument):
        return toml_source
    elif isinstance(toml_source, dict):
        return from_dict_to_toml_document(dictionary=toml_source)

    # If the source is passed as a bytes object
    elif isinstance(toml_source, bytes):
        return _load_toml(toml_content=toml_source)
    
    # In the insanely rare case where the source is passed as a bytearray object
    elif isinstance(toml_source, bytearray):
        toml_source_to_bytes = bytes(toml_source)

        return _load_toml(toml_content=toml_source_to_bytes)
    else:
        raise TypeError(f"Invalid type passed for toml_source argument")