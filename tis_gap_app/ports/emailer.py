from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmailMessage:
    subject: str
    body_html: str
    body_text: str
    to: List[str]
    from_addr: str
    attachments: Optional[List[str]] = None


class EmailerPort(ABC):

    @abstractmethod
    def send(self, message: EmailMessage) -> bool:
        ...