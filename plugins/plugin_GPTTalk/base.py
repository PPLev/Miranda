import datetime

import peewee as pw

db = pw.SqliteDatabase('GPT.db')


class Base(pw.Model):
    class Meta:
        database = db


class ContextHistory(Base):
    id = pw.IntegerField(primary_key=True)
    # time = pw.DateField()
    role = pw.TextField(null=True)
    content = pw.TextField(null=True)

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
        database = db


