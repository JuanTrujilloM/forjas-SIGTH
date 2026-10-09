# external libraries imports
from dataclasses import dataclass


# main class
@dataclass(frozen=True)
class EmployeeExportColumn:
    key: str
    label: str
    kind: str = 'text'
    source: str | None = None
