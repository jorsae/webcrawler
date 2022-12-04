import peewee as pw
from models import BaseModel, UrlStatusModel

class DomainModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    domain = pw.TextField()
    url_status_id = pw.ForeignKeyField(UrlStatusModel, to_field='id')

    class Meta:
        table_name = 'Domain'