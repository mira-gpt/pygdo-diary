# Diary

A small PyGDO diary / blog module. Each user has one entry per UTC day, with
separately timestamped paragraphs in chronological order. A new day is private
by default and can be explicitly marked public. The per-user setting
`diary_default_public` changes the default for new days; existing days are not
changed. The listing shows public days
and, to an authenticated user, their own private days (up to 100 days).
Staff can enable the `diary_sidebar_user` user configuration to add a sidebar
link to a user's diary when that user has at least one public day. Multiple
users may be featured. Links do not expose private days to other visitors.

Install the module with PyGDO's module installer, then visit `diary.write` to
append a paragraph and `diary.entries` to read. The title and public checkbox
apply only when creating that day's entry; later writes never change them. An
empty title defaults to the date. This version does not provide editing,
deletion, comments or subscriptions.

`diary.newday <title>` creates today's day using that default, without a paragraph. In
chat, use it in a private conversation and quote titles containing spaces. It
does not overwrite or retitle an existing day. Currently `diary.write` is web
only; its first paragraph can also create the day if needed.

Do not store passwords, tokens or other secrets in entries. Like other PyGDO
data, private entries are accessible to server and database administrators.
