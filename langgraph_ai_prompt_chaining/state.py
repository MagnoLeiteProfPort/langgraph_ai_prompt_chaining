from typing_extensions import TypedDict


class State(TypedDict, total=False):
    topic: str
    letter: str
    word: str
    phrase: str
    relevant: bool  # set by the checker
