import peewee as pw

from models import BaseModel, CrawlHistoryModel


class CrawlDataModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    data = pw.TextField()
    crawl_history_id = pw.ForeignKeyField(CrawlHistoryModel, to_field="id")

    class Meta:
        table_name = "CrawlData"
