# Diary

A small PyGDO diary / blog module. Signed-in users can write entries; entries
are private by default and may be explicitly marked public. The listing shows
public entries and, to an authenticated user, their own private entries.

Install the module with PyGDO's module installer, then visit `diary.write` to
write and `diary.entries` to read. Publishing is an explicit choice. This first
version does not provide editing, deletion, comments or subscriptions.

Do not store passwords, tokens or other secrets in entries. Like other PyGDO
data, private entries are accessible to server and database administrators.
