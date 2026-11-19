from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Unique import GDT_Unique
from gdo.date.GDT_Date import GDT_Date


class GDO_DiaryEntry(GDO):
    """One owner's diary day. Paragraphs live in a separate table."""

    def gdo_columns(self):
        return [
            GDT_AutoInc('entry_id'),
            GDT_String('entry_title').not_null().minlen(1).maxlen(160),
            GDT_Date('entry_date').not_null(),
            GDT_Bool('entry_public').not_null().initial('0'),
            GDT_Creator('entry_creator'),
            GDT_Unique('diary_owner_day').unique_columns('entry_creator', 'entry_date'),
        ]
