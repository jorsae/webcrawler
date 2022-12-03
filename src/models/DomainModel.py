import peewee as pw
from models import BaseModel

class DomainModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    domain = pw.TextField()

    class Meta:
        table_name = 'Domain'