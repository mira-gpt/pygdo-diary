from gdo.base.GDO import GDO
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_Text import GDT_Text
from gdo.date.GDT_Created import GDT_Created
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry


class GDO_DiaryParagraph(GDO):
    def gdo_columns(self):
        return [
            GDT_AutoInc('paragraph_id'),
            GDT_Object('paragraph_entry').table(GDO_DiaryEntry.table()).not_null().cascade_delete(),
            GDT_Text('paragraph_body').not_null().minlen(1).maxlen(4096),
            GDT_Created('paragraph_created'),
        ]
