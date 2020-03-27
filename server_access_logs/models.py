from django.db import models

class AccessLogsModel(models.Model):
    sys_id = models.AutoField(primary_key=True, null=False, blank=True)
    session_key = models.CharField(max_length=1024, null=False, blank=True)
    request_path = models.CharField(max_length=1024, null=False, blank=True)
    request_method = models.CharField(max_length=8, null=False, blank=True)
    request_data = models.TextField(null=True, blank=True)
    request_ip_address = models.CharField(max_length=45, null=False, blank=True)
    request_referrer = models.CharField(max_length=512, null=True, blank=True)
    request_timestamp = models.DateTimeField(null=False, blank=True)

    response_status = models.CharField(max_length=8, null=False, blank=True)
    response_timestamp = models.DateTimeField(null=False, blank=True)

    processed_time = models.CharField(max_length=8, null=False, blank=True)
    
    def __str__(self):
        obj_dict = vars(self)
        if "_state" in obj_dict:
            del obj_dict["_state"]
        return str(obj_dict)

    class Meta:
        app_label = "server_access_logs"
        db_table = "access_logs"
