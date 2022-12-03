import peewee as pw
from models import BaseModel, DomainModel

class CrawlHistoryModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    url = pw.TextField()
    timestamp = pw.DateTimeField()
    status_code = pw.SmallIntegerField()
    domain_id = pw.ForeignKeyField(DomainModel, to_field='id')

    class Meta:
        table_name = 'CrawlHistory'