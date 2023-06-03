from django.contrib import admin

# Register your models here.
import pprint
from django.contrib.sessions.models import Session
#* from .models import UploadedFile

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return pprint.pformat(obj.get_decoded()).replace('\n', '<br>\n')
    _session_data.allow_tags=True
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
    exclude = ['session_data']
    date_hierarchy='expire_date'
admin.site.register(Session, SessionAdmin)

"""
#*
@admin.register(UploadedFile)
class FileAdmin(admin.ModelAdmin):
    readonly_fields=('md5_checksum', 'normalized')
"""
