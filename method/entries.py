import html

from gdo.base.Method import Method
from gdo.core.GDT_UInt import GDT_UInt
from gdo.diary.GDO_DiaryEntry import GDO_DiaryEntry
from gdo.diary.GDO_DiaryParagraph import GDO_DiaryParagraph
from gdo.message.GDT_HTML import GDT_HTML


class entries(Method):
    """Display public days and the authenticated visitor's own days."""

    def gdo_needs_authentication(self):
        return False

    def gdo_connectors(self):
        return 'web'

    def gdo_parameters(self):
        return [GDT_UInt('owner').min(1).not_null(False)]

    def gdo_execute(self):
        user = self._env_user
        where = 'entry_public=1'
        if user and user.is_authenticated():
            where += f' OR entry_creator={int(user.get_id())}'
        query = GDO_DiaryEntry.table().select().nocache().where(where)
        owner = self.param_val('owner')
        if owner:
            query.where(f'entry_creator={int(owner)}')
        days = query.order(
            'entry_date DESC, entry_id DESC').take(100).exec()
        sections = []
        for day in days:
            day_id = int(day.get_id())
            paragraphs = GDO_DiaryParagraph.table().select().nocache().where(
                f'paragraph_entry={day_id}').order('paragraph_created ASC, paragraph_id ASC').exec()
            parts = []
            for paragraph in paragraphs:
                stamp = html.escape(str(paragraph.gdo_val('paragraph_created') or ''))
                body = html.escape(str(paragraph.gdo_val('paragraph_body') or ''))
                parts.append(f'<p><time>{stamp} UTC</time><br>{body}</p>')
            title = html.escape(str(day.gdo_val('entry_title') or ''))
            date = html.escape(str(day.gdo_val('entry_date') or ''))
            sections.append(f'<section><h2>{title}</h2><p>{date} (UTC)</p>{"".join(parts)}</section>')
        return GDT_HTML().html(''.join(sections))
