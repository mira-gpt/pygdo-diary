import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.diary.GDO_DiaryParagraph import GDO_DiaryParagraph
from gdo.diary.method.entries import entries
from gdo.diary.method.write import write
from gdo.diary.method.newday import newday
from gdo.diary.module_diary import module_diary


class DiaryTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_html)

    def test_private_by_default(self):
        creator = MagicMock()
        creator.get_name.return_value = 'entry_creator'
        with patch('gdo.diary.GDO_DiaryEntry.GDT_Creator', return_value=creator):
            fields = {field.get_name(): field for field in GDO_DiaryEntry().gdo_columns()}
        self.assertEqual('0', fields['entry_public'].get_initial())

    def test_user_setting_is_private_by_default(self):
        setting = module_diary().gdo_user_settings()[0]
        self.assertEqual('diary_default_public', setting.get_name())
        self.assertEqual('0', setting.get_initial())

    def test_sidebar_flag_is_staff_user_config_and_off_by_default(self):
        setting = module_diary().gdo_user_config()[0]
        self.assertEqual('diary_sidebar_user', setting.get_name())
        self.assertEqual('0', setting.get_initial())

    def test_owner_filter_keeps_guest_public_only(self):
        method = entries()
        method._env_user = None
        method.input('owner', '42')
        table = MagicMock()
        query = table.select.return_value.nocache.return_value
        query.where.return_value = query
        query.order.return_value.take.return_value.exec.return_value = []
        with patch.object(GDO_DiaryEntry, 'table', return_value=table):
            method.gdo_execute()
        self.assertEqual(['entry_public=1', 'entry_creator=42'],
                         [call.args[0] for call in query.where.call_args_list])

    def test_write_form_prefills_user_visibility(self):
        for value in ('0', '1'):
            with self.subTest(value=value):
                method = write()
                method._env_user = MagicMock()
                method._env_user.get_setting_val.return_value = value
                form = MagicMock()
                with patch('gdo.form.MethodForm.MethodForm.gdo_create_form'):
                    method.gdo_create_form(form)
                fields = form.add_fields.call_args.args
                public = next(field for field in fields if field.get_name() == 'public')
                self.assertEqual(value, public.get_initial())

    def test_guest_sees_only_public_entries(self):
        method = entries()
        method._env_user = MagicMock()
        method._env_user.is_authenticated.return_value = False
        table = MagicMock()
        query = table.select.return_value.nocache.return_value
        query.where.return_value.order.return_value.take.return_value.exec.return_value = []
        with patch.object(GDO_DiaryEntry, 'table', return_value=table):
            method.gdo_execute()
        query.where.assert_called_once_with('entry_public=1')

    def test_member_sees_public_and_own_entries(self):
        method = entries()
        method._env_user = MagicMock()
        method._env_user.is_authenticated.return_value = True
        method._env_user.get_id.return_value = '42'
        table = MagicMock()
        query = table.select.return_value.nocache.return_value
        query.where.return_value.order.return_value.take.return_value.exec.return_value = []
        with patch.object(GDO_DiaryEntry, 'table', return_value=table):
            method.gdo_execute()
        query.where.assert_called_once_with('entry_public=1 OR entry_creator=42')

    def test_append_uses_existing_day_without_changing_its_visibility(self):
        method = write()
        method._env_user = MagicMock()
        method._env_user.get_id.return_value = '42'
        form = MagicMock()
        form.get_field.return_value.get_val.return_value = 'A paragraph'
        day = MagicMock()
        day.get_id.return_value = '7'
        table = MagicMock()
        table.get_by_vals.return_value = day
        with patch.object(write, 'get_form', return_value=form), \
             patch('gdo.diary.method.write.Time.get_date_without_time', return_value='2026-11-18'), \
             patch('gdo.diary.method.write.DBLock'), \
             patch.object(GDO_DiaryEntry, 'table', return_value=table), \
             patch.object(GDO_DiaryEntry, 'blank') as new_day, \
             patch.object(GDO_DiaryParagraph, 'blank') as paragraph, \
             patch.object(write, 'msg'):
            method.form_submitted()
        new_day.assert_not_called()
        paragraph.assert_called_once_with({'paragraph_entry': '7', 'paragraph_body': 'A paragraph'})
        paragraph.return_value.insert.assert_called_once()

    def test_first_paragraph_creates_day_then_appends(self):
        method = write()
        method._env_user = MagicMock()
        method._env_user.get_id.return_value = '42'
        form = MagicMock()
        values = {'title': '', 'public': '0', 'body': 'First paragraph'}
        form.get_field.side_effect = lambda name: MagicMock(get_val=MagicMock(return_value=values[name]))
        table = MagicMock()
        table.get_by_vals.return_value = None
        with patch.object(write, 'get_form', return_value=form), \
             patch('gdo.diary.method.write.Time.get_date_without_time', return_value='2026-11-18'), \
             patch('gdo.diary.method.write.DBLock'), \
             patch.object(GDO_DiaryEntry, 'table', return_value=table), \
             patch.object(GDO_DiaryEntry, 'blank') as new_day, \
             patch.object(GDO_DiaryParagraph, 'blank') as paragraph, \
             patch.object(write, 'msg'):
            new_day.return_value.insert.return_value.get_id.return_value = '7'
            method.form_submitted()
        new_day.assert_called_once_with({'entry_title': '2026-11-18', 'entry_date': '2026-11-18',
                                         'entry_public': '0', 'entry_creator': '42'})
        paragraph.assert_called_once_with({'paragraph_entry': '7', 'paragraph_body': 'First paragraph'})

    def test_day_output_escapes_paragraph_text(self):
        method = entries()
        method._env_user = None
        day = MagicMock()
        day.get_id.return_value = '7'
        day.gdo_val.side_effect = lambda name: {'entry_title': '<script>', 'entry_date': '2026-11-18'}[name]
        paragraph = MagicMock()
        paragraph.gdo_val.side_effect = lambda name: {'paragraph_body': '<img>', 'paragraph_created': '10:00'}[name]
        day_table, paragraph_table = MagicMock(), MagicMock()
        day_table.select.return_value.nocache.return_value.where.return_value.order.return_value.take.return_value.exec.return_value = [day]
        paragraph_table.select.return_value.nocache.return_value.where.return_value.order.return_value.exec.return_value = [paragraph]
        with patch.object(GDO_DiaryEntry, 'table', return_value=day_table), \
             patch.object(GDO_DiaryParagraph, 'table', return_value=paragraph_table):
            rendered = method.gdo_execute().render_html()
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('&lt;img&gt;', rendered)
        self.assertNotIn('<script>', rendered)

    def test_write_requires_authentication(self):
        self.assertTrue(write.gdo_needs_authentication(None))

    def test_newday_is_authenticated_and_private_in_chat(self):
        method = newday()
        self.assertTrue(method.gdo_needs_authentication())
        self.assertFalse(method.gdo_in_channels())

    def test_newday_does_not_overwrite_existing_day(self):
        method = newday()
        method._env_user = MagicMock()
        method._env_user.get_id.return_value = '42'
        table = MagicMock()
        table.get_by_vals.return_value = MagicMock()
        with patch('gdo.diary.method.newday.Time.get_date_without_time', return_value='2026-11-18'), \
             patch('gdo.diary.method.newday.DBLock'), \
             patch.object(GDO_DiaryEntry, 'table', return_value=table), \
             patch.object(GDO_DiaryEntry, 'blank') as blank, \
             patch.object(newday, 'err') as error:
            method.form_submitted()
        blank.assert_not_called()
        error.assert_called_once_with('err_diary_day_exists')

    def test_newday_creates_private_day(self):
        method = newday()
        method._env_user = MagicMock()
        method._env_user.get_id.return_value = '42'
        method._env_user.get_setting_val.return_value = '0'
        table = MagicMock()
        table.get_by_vals.return_value = None
        form = MagicMock()
        form.get_field.return_value.get_val.return_value = 'My day'
        with patch('gdo.diary.method.newday.Time.get_date_without_time', return_value='2026-11-18'), \
             patch('gdo.diary.method.newday.DBLock'), \
             patch.object(GDO_DiaryEntry, 'table', return_value=table), \
             patch.object(GDO_DiaryEntry, 'blank') as blank, \
             patch.object(newday, 'get_form', return_value=form), \
             patch.object(newday, 'msg'):
            method.form_submitted()
        blank.assert_called_once_with({'entry_title': 'My day', 'entry_date': '2026-11-18',
                                       'entry_public': '0', 'entry_creator': '42'})
        blank.return_value.insert.assert_called_once()

    def test_newday_uses_public_user_default(self):
        method = newday()
        method._env_user = MagicMock()
        method._env_user.get_id.return_value = '42'
        method._env_user.get_setting_val.return_value = '1'
        table = MagicMock()
        table.get_by_vals.return_value = None
        form = MagicMock()
        form.get_field.return_value.get_val.return_value = 'My day'
        with patch('gdo.diary.method.newday.Time.get_date_without_time', return_value='2026-11-18'), \
             patch('gdo.diary.method.newday.DBLock'), \
             patch.object(GDO_DiaryEntry, 'table', return_value=table), \
             patch.object(GDO_DiaryEntry, 'blank') as blank, \
             patch.object(newday, 'get_form', return_value=form), \
             patch.object(newday, 'msg'):
            method.form_submitted()
        self.assertEqual('1', blank.call_args.args[0]['entry_public'])

    def test_get_never_submits_entry(self):
        method = write()
        with patch.object(Application, 'IS_HTTP', True), \
             patch.object(Application, 'get_request_method', return_value='GET'), \
             patch.object(write, 'parameters'), patch.object(write, 'render_page') as page, \
             patch.object(write, 'form_submitted') as submit:
            self.assertIs(method.gdo_execute(), page.return_value)
        submit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
