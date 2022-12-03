import peewee as pw
from models import BaseModel, CrawlHistoryModel

class CrawlEmailModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    email = pw.TextField()
    timestamp = pw.DateTimeField()
    crawl_history_id = pw.ForeignKeyField(CrawlHistoryModel, to_field='id')

    class Meta:
        table_name = 'CrawlEmail'