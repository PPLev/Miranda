import datetime

import peewee as pw

db = pw.SqliteDatabase('notice.db')


class Base(pw.Model):
    class Meta:
        database = db


class Dir(Base):
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField(max_length=50, null=False, default="Новая папка")
    parent = pw.ForeignKeyField('self', backref="childs", null=True)

    def to_dict(self):
        return {
            "id": self.id,
            "directory": self.name,
            "notes": [note.to_dict() for note in self.notes]
        }

    def tree(self, indent=2):
        data = []
        data.append(f'{" " * indent}{self.value}{"/" if len(self.childs) else ""}\n')
        for i in self.childs:
            data.append(i.tree(indent + 2))
            # data.append(f'{" "*indent}{i.tree(indent+2)}\n')
        return "".join(data)

    def delete(self):
        for child in self.cilds:
            child.delete()

        for note in self.notes:
            note.delete()

        self.delete_instance()

    @property
    def notes_list(self):
        return [note.value for note in self.notes]

    class Meta:
        table_name = "directories"


class Note(Base):
    id = pw.IntegerField(primary_key=True)
    value = pw.TextField(null=False)
    dir = pw.ForeignKeyField(Dir, backref="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "directory": self.dir,
            "value": self.value
        }

    def delete(self):
        self.delete_instance()

    class Meta:
        table_name = "notes"


db.connect()
db.create_tables([Dir, Note])
