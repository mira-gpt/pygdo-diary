from gdo.base.GDO_Module import GDO_Module
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.ui.GDT_Link import GDT_Link


class module_diary(GDO_Module):
    """Personal diary entries with optional public visibility."""

    def gdo_classes(self):
        return [GDO_DiaryEntry]

    def gdo_main_method_name(self):
        return 'entries'

    def gdo_init_sidebar(self, page):
        page._left_bar.add_field(GDT_Link().href(self.href('entries')).text('mt_diary_entries'))
        page._left_bar.add_field(GDT_Link().href(self.href('write')).text('mt_diary_write'))
