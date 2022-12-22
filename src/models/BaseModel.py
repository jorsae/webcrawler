import peewee as pw
import constants

database = pw.SqliteDatabase(None)

class BaseModel(pw.Model):
    class Meta:
        database = database