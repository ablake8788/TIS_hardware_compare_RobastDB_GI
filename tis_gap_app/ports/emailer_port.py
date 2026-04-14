"""
Port: abstract interface for email sending.
Services depend only on this port — never on the concrete adapter.
"""
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
    attachments: Optional[List[str]] = None  # file paths


class EmailerPort(ABC):
    """Abstract interface for sending email notifications."""

    @abstractmethod
    def send(self, message: EmailMessage) -> bool:
        """Send email. Returns True on success, False on failure."""
        ...
