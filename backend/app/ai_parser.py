"""
Stub for the AI email parser.

This module is intended to be replaced by a real machine learning or
LLM integration. It currently contains a simple function that
extracts a potential order title from an email subject line and
returns a dictionary compatible with the OrderCreate schema.

When implementing a real parser, consider using large language
models, HuggingFace transformers or fine‑tuned classification models
to detect order types, quantities and customer information. For now,
the parser simply returns the entire subject as the order title.
"""

from typing import Dict


def parse_email(subject: str, body: str) -> Dict[str, str]:
    """Parse an email into an order representation.

    Args:
        subject: The subject line of the email.
        body: The plain text body of the email.

    Returns:
        A dictionary with keys compatible with the OrderCreate schema
        (title, details). In the absence of a real parser, the title
        is taken from the subject and the details from the body.
    """
    return {
        "title": subject.strip() or "Untitled Order",
        "details": body.strip() or None,
    }
