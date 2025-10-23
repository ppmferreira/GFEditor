from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Item:
    """Represents an item row from the data file.

    Stores some common fields as attributes and keeps all columns in the
    `extra` dict so no data is lost.
    """

    Id: Optional[int] = None
    Name: Optional[str] = None
    IconFilename: Optional[str] = None
    ModelId: Optional[int] = None
    ModelFilename: Optional[str] = None
    ItemType: Optional[str] = None
    EquipType: Optional[str] = None
    SysPrice: Optional[int] = None
    MaxStack: Optional[int] = None
    Tip: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_row(cls, header: List[str], row: List[str]) -> 'Item':
        """Create an Item from a header and a row (list of values).

        Attempts to convert numeric-looking values to int automatically.
        Non-numeric values (including BIG5-encoded Chinese names) are kept
        as strings. All parsed values are placed in `extra` as a dict from
        column name to typed value. A few common fields are also copied to
        top-level attributes for convenience.
        """
        data: Dict[str, Any] = {}
        for h, v in zip(header, row):
            if v is None or v == '':
                data[h] = None
            else:
                s = v.strip()
                # treat as integer when the string contains only digits
                if s.lstrip('-').isdigit():
                    try:
                        data[h] = int(s)
                    except Exception:
                        data[h] = s
                else:
                    data[h] = s

        item = cls(
            Id=data.get('Id'),
            Name=data.get('Name'),
            IconFilename=data.get('IconFilename'),
            ModelId=data.get('ModelId'),
            ModelFilename=data.get('ModelFilename'),
            ItemType=data.get('ItemType'),
            EquipType=data.get('EquipType'),
            SysPrice=data.get('SysPrice'),
            MaxStack=data.get('MaxStack'),
            Tip=data.get('Tip'),
            extra=data,
        )
        return item
