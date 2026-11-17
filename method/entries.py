from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.table.MethodQueryTable import MethodQueryTable


class entries(MethodQueryTable):
    """Public entries plus the authenticated visitor's private entries."""

    def gdo_needs_authentication(self):
        return False

    def gdo_table(self):
        return GDO_DiaryEntry.table()

    def gdo_table_headers(self):
        table = self.gdo_table()
        return [table.column(name) for name in
                ('entry_title', 'entry_body', 'entry_creator', 'entry_created')]

    def gdo_table_query(self):
        query = self.gdo_table().select().nocache()
        user = self._env_user
        if user and user.is_authenticated():
            owner = int(user.get_id())
            return query.where(f'entry_public=1 OR entry_creator={owner}')
        return query.where('entry_public=1')

    def gdo_order_default(self):
        return 'entry_created DESC, entry_id DESC'
