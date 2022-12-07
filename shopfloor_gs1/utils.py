# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from biip.gs1 import GS1Message

AI_MAPPING = (
    # https://www.gs1.org/standards/barcodes/application-identifiers
    ("01", "product"),
    ("10", "lot"),
    ("11", "production_date"),
)


class GS1Barcode:
    """TODO"""

    __slots__ = ("ai", "type", "code", "value", "raw_value")

    def __init__(self, **kw) -> None:
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.type}>"

    def __bool__(self):
        return self.type != "none" or bool(self.record)

    def __eq__(self, other):
        for k in self.__slots__:
            if not hasattr(other, k):
                return False
            if getattr(other, k) != getattr(self, k):
                return False
        return True

    @classmethod
    def parse(cls, barcode, ai_whitelist=None, ai_mapping=AI_MAPPING):
        """TODO"""
        # TODO: we might not get an HRI...
        parsed = GS1Message.parse_hri(barcode)
        if not parsed:
            return None
        res = []
        for ai, record_type in ai_mapping:
            if ai_whitelist and ai not in ai_whitelist:
                continue
            found = parsed.get(ai=ai)
            if found:
                # when value is a date the datetime obj is in `date`
                # TODO: other types have their own special key
                value = found.date or found.value
                info = cls(
                    ai=ai,
                    type=record_type,
                    code=barcode,
                    raw_value=found.value,
                    value=value,
                )
                res.append(info)
        return res
