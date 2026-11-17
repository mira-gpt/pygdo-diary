from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text
from gdo.date.GDT_Created import GDT_Created


class GDO_DiaryEntry(GDO):
    def gdo_columns(self):
        return [
            GDT_AutoInc('entry_id'),
            GDT_String('entry_title').not_null().minlen(1).maxlen(160),
            GDT_Text('entry_body').not_null().maxlen(4096),
            GDT_Bool('entry_public').not_null().initial('0'),
            GDT_Creator('entry_creator'),
            GDT_Created('entry_created'),
        ]
