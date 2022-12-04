import peewee as pw
from models import BaseModel

class RequestStatusModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    request_status = pw.TextField()

    class Meta:
        table_name = 'RequestStatus'