import peewee as pw

database = pw.SqliteDatabase(None, check_same_thread=False)


class BaseModel(pw.Model):
    class Meta:
        database = database
