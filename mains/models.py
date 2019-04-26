from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FileManagement(models.Model):
	uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="file_management")
	file = models.FileField(upload_to="media/", blank=False)
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "files_management"

	def __str__(self):
		return self.file.name


class FileManagementType(models.Model):
	type = models.CharField(max_length=255)
	label = models.CharField(max_length=255, null=True)
	is_active = models.NullBooleanField()

	class Meta:
		db_table = "files_management_type"

	def __str__(self):
		return self.type
