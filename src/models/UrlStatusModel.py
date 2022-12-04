import peewee as pw
from models import BaseModel

class UrlStatusModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    url_status = pw.TextField()

    class Meta:
            table_name = 'UrlStatus'