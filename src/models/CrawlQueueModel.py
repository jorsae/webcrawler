import peewee as pw

from models import BaseModel, DomainModel


class CrawlQueueModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    url = pw.TextField(unique=True)
    priority = pw.SmallIntegerField()
    timestamp = pw.DateTimeField()
    domain_id = pw.ForeignKeyField(DomainModel, to_field="id")

    class Meta:
        table_name = "CrawlQueue"
