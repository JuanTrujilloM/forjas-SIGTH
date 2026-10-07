# external libraries imports
from dataclasses import dataclass


# main class
@dataclass(frozen=True)
class EmployeeExportColumn:
    key: str
    label: str
    # text, choice, boolean, date, money, integer, relation, seniority or extensions
    kind: str = 'text'
    source: str | None = None
