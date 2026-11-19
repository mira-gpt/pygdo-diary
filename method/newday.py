from gdo.base.Application import Application
from gdo.base.DBLock import DBLock
from gdo.core.GDT_String import GDT_String
from gdo.date.Time import Time
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.form.MethodForm import MethodForm


class newday(MethodForm):
    """Create today's diary day; do not replace an existing day."""

    def gdo_in_channels(self):
        return False

    def gdo_create_form(self, form):
        form.add_field(GDT_String('title').not_null().minlen(1).maxlen(160).positional().label('entry_title'))
        super().gdo_create_form(form)

    def gdo_execute(self):
        if Application.IS_HTTP and Application.get_request_method() != 'POST':
            self.parameters()
            return self.render_page()
        return super().gdo_execute()

    def form_submitted(self):
        owner = int(self._env_user.get_id())
        date = Time.get_date_without_time()
        with DBLock(f'diary:{owner}:{date}'):
            existing = GDO_DiaryEntry.table().get_by_vals({
                'entry_creator': str(owner), 'entry_date': date,
            })
            if existing:
                return self.err('err_diary_day_exists')
            GDO_DiaryEntry.blank({
                'entry_title': self.get_form().get_field('title').get_val(),
                'entry_date': date,
                'entry_public': self._env_user.get_setting_val('diary_default_public'),
                'entry_creator': str(owner),
            }).insert()
        return self.msg('msg_diary_day_created')
