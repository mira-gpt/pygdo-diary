import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.base.Render import Mode
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.diary.method.entries import entries
from gdo.diary.method.write import write


class DiaryTest(unittest.TestCase):
    def setUp(self):
        Application.mode(Mode.render_html)

    def test_private_by_default(self):
        creator = MagicMock()
        creator.get_name.return_value = 'entry_creator'
        with patch('gdo.diary.GDO_DiaryEntry.GDT_Creator', return_value=creator):
            fields = {field.get_name(): field for field in GDO_DiaryEntry().gdo_columns()}
        self.assertEqual('0', fields['entry_public'].get_initial())

    def test_guest_sees_only_public_entries(self):
        method = entries()
        method._env_user = MagicMock()
        method._env_user.is_authenticated.return_value = False
        table = MagicMock()
        query = table.select.return_value.nocache.return_value
        with patch.object(entries, 'gdo_table', return_value=table):
            method.gdo_table_query()
        query.where.assert_called_once_with('entry_public=1')

    def test_member_sees_public_and_own_entries(self):
        method = entries()
        method._env_user = MagicMock()
        method._env_user.is_authenticated.return_value = True
        method._env_user.get_id.return_value = '42'
        table = MagicMock()
        query = table.select.return_value.nocache.return_value
        with patch.object(entries, 'gdo_table', return_value=table):
            method.gdo_table_query()
        query.where.assert_called_once_with('entry_public=1 OR entry_creator=42')

    def test_write_requires_authentication(self):
        self.assertTrue(write.gdo_needs_authentication(None))

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
