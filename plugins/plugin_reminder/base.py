import datetime

import peewee as pw

db = pw.SqliteDatabase('notice.db')


class Base(pw.Model):
    class Meta:
        database = db


class Notice(Base):
    id = pw.IntegerField(primary_key=True)
    value = pw.TextField(null=True)
    create_date = pw.DateTimeField(default=datetime.datetime.now)
    remind_date = pw.DateTimeField(null=True)

    @staticmethod
    def get_next_day_notice():
        notises = Notice.select().were(Notice.create_date.day)

    @staticmethod
    def get_next_week_notice():
        notises = Notice.select().were(Notice.create_date.day)

    @staticmethod
    def new_notice():
        notises = Notice.select().were(Notice.create_date.day)

    @staticmethod
    def get_future_notices(future_hour: int):
        tz = datetime.timezone(datetime.timedelta(hours=3), name='МСК')
        finish_time = datetime.datetime.now(tz=tz) + datetime.timedelta(hours=future_hour)
        notices = Notice.select().where(
            (Notice.remind_date > datetime.datetime.now()) & (Notice.remind_date < finish_time)
        )
        return notices


db.connect()
db.create_tables([Notice])
