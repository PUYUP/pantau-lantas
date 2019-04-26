from django.contrib import admin

# Register your models here.
from mains.models import FileManagement, FileManagementType

# Extending list display
class FileManagementDisplay(admin.ModelAdmin):
	"""
	Tampilkan field lain file management
	"""
	list_display = ('uploader', 'file', 'timestamp')

# Show to admin
admin.site.register(FileManagement, FileManagementDisplay)
admin.site.register(FileManagementType)
