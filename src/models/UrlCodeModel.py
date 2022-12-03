import peewee as pw
from models import BaseModel

class UrlCodeModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    url_code = pw.TextField()

    class Meta:
        table_name = 'UrlCode'