"""
Periodic email polling script for Grafline Tracking.

This script connects to an IMAP server using credentials supplied
via environment variables and imports unseen messages as new orders.
It leverages the `ai_parser` to extract order information from
emails. When running in Render, schedule this script via a cron
service. Locally, you can run it manually to import orders.
"""

import os
import imaplib
import email
from email.header import decode_header
import traceback

from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Order, OrderStatus, Base
from .ai_parser import parse_email


def connect_imap():
    """Connect to the IMAP server using environment variables.

    Returns:
        A connected IMAP4_SSL instance.
    """
    host = os.environ.get("IMAP_HOST")
    port = int(os.environ.get("IMAP_PORT", "993"))
    username = os.environ.get("IMAP_USERNAME")
    password = os.environ.get("IMAP_PASSWORD")
    if not all([host, username, password]):
        raise RuntimeError(
            "IMAP credentials are not fully configured. "
            "Please set IMAP_HOST, IMAP_PORT, IMAP_USERNAME and IMAP_PASSWORD."
        )
    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(username, password)
    return mail


def fetch_unseen_messages(mail):
    """Yield unseen messages from the INBOX folder."""
    mail.select("INBOX")
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        return []
    for num in messages[0].split():
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            continue
        msg = email.message_from_bytes(data[0][1])
        yield msg
        # Mark message as seen
        mail.store(num, '+FLAGS', '\\Seen')


def decode_mime_words(s):
    """Decode MIME encoded words in a header to a UTF‑8 string."""
    decoded = ''
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            decoded += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded += part
    return decoded


def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    mail = None
    try:
        mail = connect_imap()
        for msg in fetch_unseen_messages(mail):
            subject = decode_mime_words(msg.get('Subject', ''))
            body = ''
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        charset = part.get_content_charset() or 'utf-8'
                        body += part.get_payload(decode=True).decode(charset, errors='ignore')
            else:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')

            order_data = parse_email(subject, body)
            with SessionLocal() as db:
                order = Order(
                    title=order_data.get('title', 'Untitled Order'),
                    details=order_data.get('details'),
                    status=OrderStatus.NEW,
                )
                db.add(order)
                db.commit()
                db.refresh(order)
                print(f"Imported new order {order.id}: {order.title}")
    except Exception as e:
        traceback.print_exc()
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


if __name__ == "__main__":
    main()
