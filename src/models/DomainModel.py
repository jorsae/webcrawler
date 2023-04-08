import peewee as pw
from models import BaseModel, UrlStatusModel

import constants

class DomainModel(BaseModel):
    id = pw.AutoField(primary_key=True)
    domain = pw.TextField()
    with constants.URL_STATUS_MODEL_LOCK:
        url_status_id = pw.ForeignKeyField(UrlStatusModel, to_field='id', default=4)

    class Meta:
        table_name = 'Domain'