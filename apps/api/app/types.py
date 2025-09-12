# apps/api/app/types.py
# Tek kaynak: SourceType. Monorepo'da packages varsa onu kullan, yoksa yerel enum.
try:
    from packages.shared.schemas import SourceType  # type: ignore
except Exception:
    from enum import Enum
    class SourceType(str, Enum):
        rss = "rss"
        web = "web"
        extension = "extension"
        manual = "manual"
        file = "file"

__all__ = ["SourceType"]