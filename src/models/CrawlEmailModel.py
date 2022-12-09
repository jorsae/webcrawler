import peewee as pw
from models import BaseModel

class CrawlEmailModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    email = pw.TextField(unique=True)
    timestamp = pw.DateTimeField()

    class Meta:
        table_name = 'CrawlEmail'