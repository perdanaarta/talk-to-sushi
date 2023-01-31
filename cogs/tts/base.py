from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Message:
    user: str
    text: str
    lang: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    rate: Optional[float] = None
    pitch: Optional[float] = None

    def render(self):
        result = self.user + ":"
        if self.text is not None:
            result += " " + self.text
        return result