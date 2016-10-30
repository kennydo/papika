from typing import (
    Any,
    Dict,
)


class Bridge:
    def __init__(config: Dict[str, Any]) -> None:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError
