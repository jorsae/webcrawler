import peewee as pw
import constants

database = pw.SqliteDatabase(constants.DATABASE_FILE, check_same_thread=False)

class BaseModel(pw.Model):
    class Meta:
        database = database