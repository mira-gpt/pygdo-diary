from gdo.base.Application import Application
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.form.MethodForm import MethodForm


class write(MethodForm):
    def gdo_connectors(self):
        return 'web'

    def gdo_create_form(self, form):
        form.add_fields(
            GDT_String('title').not_null().minlen(1).maxlen(160).label('entry_title'),
            GDT_Text('body').not_null().maxlen(4096).label('entry_body'),
            GDT_Bool('public').not_null().initial('0').label('entry_public'),
        )
        super().gdo_create_form(form)

    def gdo_execute(self):
        if Application.IS_HTTP and Application.get_request_method() != 'POST':
            self.parameters()
            return self.render_page()
        return super().gdo_execute()

    def form_submitted(self):
        form = self.get_form()
        GDO_DiaryEntry.blank({
            'entry_title': form.get_field('title').get_val(),
            'entry_body': form.get_field('body').get_val(),
            'entry_public': form.get_field('public').get_val(),
            'entry_creator': self._env_user.get_id(),
        }).insert()
        return self.msg('msg_diary_created')
