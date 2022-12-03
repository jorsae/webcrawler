import peewee as pw
from models import BaseModel, UrlCodeModel

class DomainModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    domain = pw.TextField()
    url_code_id = pw.ForeignKeyField(UrlCodeModel, to_field='id')

    class Meta:
        table_name = 'Domain'