import peewee as pw

from models import BaseModel, DomainModel, RequestStatusModel


class CrawlHistoryModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    url = pw.TextField()
    timestamp = pw.DateTimeField()
    http_status_code = pw.SmallIntegerField()
    request_status = pw.ForeignKeyField(RequestStatusModel, to_field="id")
    domain_id = pw.ForeignKeyField(DomainModel, to_field="id")

    class Meta:
        table_name = "CrawlHistory"
