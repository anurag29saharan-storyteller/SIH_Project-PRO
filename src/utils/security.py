"""
Security helpers: input sanitization, XSS mitigation, and PIN verification.
"""
import re
import html
import hmac
from typing import Optional


def sanitize_text(text: str, max_chars: int = 5000) -> str:
    """
    Sanitizes user-provided incident text:
    - Strips script and style tags along with their inner content
    - Strips remaining HTML/XML tags
    - Unescapes benign entities
    - Enforces length limits
    - Strips non-printable control characters
    """
    if not text:
        return ""

    # Remove script and style tags with content
    clean = re.sub(r"(?is)<script.*?</script>", "", text)
    clean = re.sub(r"(?is)<style.*?</style>", "", clean)
    # Remove remaining HTML tags
    clean = re.sub(r"<[^>]+>", "", clean)
    # Strip non-printable control characters except newline and tab
    clean = "".join(ch for ch in clean if ch in ("\n", "\t") or (32 <= ord(ch) <= 126 or ord(ch) > 127))
    # Normalize whitespace
    clean = clean.strip()
    return clean[:max_chars]


def verify_pin(provided_pin: str, expected_pin: str) -> bool:
    """Timing-attack resistant comparison for dashboard access PIN."""
    if not provided_pin or not expected_pin:
        return False
    return hmac.compare_digest(str(provided_pin).strip(), str(expected_pin).strip())


def mask_token(token: Optional[str]) -> str:
    """Returns masked token string for secure UI display (e.g. sk-****a1b2)."""
    if not token:
        return "Not Configured"
    if len(token) <= 8:
        return "********"
    return f"{token[:3]}****{token[-4:]}"
