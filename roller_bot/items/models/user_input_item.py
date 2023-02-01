from typing import Any, Callable


class UserInputItem:
    input_description: str
    placeholder: str
    min_length: int
    max_length: int
    user_input_condition: Callable[[Any], bool]
