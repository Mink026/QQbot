"""Built-in QQ expression PNG filenames -> CDN URLs (no external face_enum.txt)."""

from __future__ import annotations

# PNG basename -> image URL (same data as former face_enum.txt; edit here to extend).
_FACE_PNG_TO_URL: dict[str, str] = {
    "ExtremelyAngry.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_70520F67B37A21A9CCAAA5438035BB7E_0_0/0",
    "Captivated.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_F3FDE896E15132E708F9E3B4B272EF1D_0_0/0",
    "Crying.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_78F53B2D5B02B1C64EC9324DF977460E_0_0/0",
    "Happy.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_772F655282D017F962C15D4374266E0F_0_0/0",
    "Sad.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_5A28982583474CAEBD3C241911D0A258_0_0/0",
    "Surprised.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_BDB60462FFD1DA7A3DDC753E5C9F9BB7_0_0/0",
    "Confused.png": "https://p.qpic.cn/qq_expression/994924990/994924990_0_0_0_2E9E7C076157138B8F40D2F80F70D5EA_0_0/0",
}

_ENUM_TO_FILE_URL: dict[str, tuple[str, str]] = {
    fname.rsplit(".", 1)[0].lower(): (fname, url)
    for fname, url in _FACE_PNG_TO_URL.items()
}


def load_face_entries() -> dict[str, tuple[str, str]]:
    """
    Mapping: lowercase stem without extension, e.g. ``happy`` -> (``Happy.png``, url).
    """
    return _ENUM_TO_FILE_URL


def resolve_face(face_enum: str) -> tuple[str, str] | None:
    """Resolve user/model enum string (e.g. ``happy``, ``ExtremelyAngry``) to (filename, url)."""
    key = face_enum.strip().lower()
    if not key:
        return None
    if key.endswith(".png"):
        key = key[:-4]
    return _ENUM_TO_FILE_URL.get(key)


def list_face_enum_keys() -> list[str]:
    """Sorted lowercase enum keys for tool descriptions / errors."""
    return sorted(_ENUM_TO_FILE_URL.keys())
