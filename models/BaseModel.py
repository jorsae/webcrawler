import peewee as pw
import constants

database = pw.SqliteDatabase(constants.DATABASE_FILE)

class BaseModel(pw.Model):
    class Meta:
        database = database