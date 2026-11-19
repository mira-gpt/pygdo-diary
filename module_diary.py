from gdo.base.GDO_Module import GDO_Module
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDO_User import GDO_User
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.diary.GDO_DiaryParagraph import GDO_DiaryParagraph
from gdo.ui.GDT_Link import GDT_Link


class module_diary(GDO_Module):
    """Personal diary entries with optional public visibility."""

    def gdo_classes(self):
        return [GDO_DiaryEntry, GDO_DiaryParagraph]

    def gdo_user_settings(self):
        return [GDT_Bool('diary_default_public').not_null().initial('0')]

    def gdo_user_config(self):
        return [GDT_Bool('diary_sidebar_user').not_null().initial('0')]

    def gdo_main_method_name(self):
        return 'entries'

    def gdo_init_sidebar(self, page):
        page._left_bar.add_field(GDT_Link().href(self.href('entries')).text('mt_diary_entries'))
        page._left_bar.add_field(GDT_Link().href(self.href('write')).text('mt_diary_write'))
        for user in GDO_User.table().with_settings([('diary_sidebar_user', '=', '1')]):
            owner = int(user.get_id())
            day = GDO_DiaryEntry.table().select().nocache().where(
                f'entry_creator={owner} AND entry_public=1').order(
                'entry_date DESC, entry_id DESC').first().exec().fetch_object()
            if day:
                page._left_bar.add_field(GDT_Link().href(
                    self.href('entries', f'&owner={owner}')
                ).text('diary_sidebar_entry', (user.render_name(),)))
