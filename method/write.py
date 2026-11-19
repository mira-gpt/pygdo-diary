from gdo.base.Application import Application
from gdo.base.DBLock import DBLock
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.diary.GDO_DiaryParagraph import GDO_DiaryParagraph
from gdo.date.Time import Time
from gdo.form.MethodForm import MethodForm


class write(MethodForm):
    def gdo_connectors(self):
        return 'web'

    def gdo_create_form(self, form):
        form.add_fields(
            GDT_String('title').maxlen(160).label('entry_title'),
            GDT_Text('body').not_null().minlen(1).maxlen(4096).label('entry_body'),
            GDT_Bool('public').not_null().initial(
                self._env_user.get_setting_val('diary_default_public')
            ).label('entry_public'),
        )
        super().gdo_create_form(form)

    def gdo_execute(self):
        if Application.IS_HTTP and Application.get_request_method() != 'POST':
            self.parameters()
            return self.render_page()
        return super().gdo_execute()

    def form_submitted(self):
        form = self.get_form()
        owner = int(self._env_user.get_id())
        date = Time.get_date_without_time()
        # Concurrent writes for the same owner/day must share one day record.
        with DBLock(f'diary:{owner}:{date}'):
            day = GDO_DiaryEntry.table().get_by_vals({
                'entry_creator': str(owner), 'entry_date': date,
            })
            if not day:
                day = GDO_DiaryEntry.blank({
                    'entry_title': form.get_field('title').get_val() or date,
                    'entry_date': date,
                    'entry_public': form.get_field('public').get_val(),
                    'entry_creator': str(owner),
                }).insert()
            GDO_DiaryParagraph.blank({
                'paragraph_entry': day.get_id(),
                'paragraph_body': form.get_field('body').get_val(),
            }).insert()
        return self.msg('msg_diary_created')
