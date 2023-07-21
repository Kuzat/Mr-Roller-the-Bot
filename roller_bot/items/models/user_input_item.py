from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class UserInputOptions:
    input_description: str
    placeholder: str
    min_length: int
    max_length: int
    user_input_condition: Callable[[Any], bool]
