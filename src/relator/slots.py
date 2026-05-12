from __future__ import annotations
import re
from collections.abc import Mapping
from .errors import TemplateError
SLOT_RE = re.compile('@@([A-Za-z0-9_]+)@@')

def replace_slots(text: str, slots: Mapping[str, str]) -> str:
    found = set(SLOT_RE.findall(text))
    missing = found - slots.keys()
    if missing:
        names = ', '.join(sorted(missing))
        raise TemplateError(f'Missing slot value(s) for: {names}')

    def _sub(match: re.Match[str]) -> str:
        return slots[match.group(1)]
    return SLOT_RE.sub(_sub, text)
