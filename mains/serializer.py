from rest_framework import serializers

from mains.models import FileManagement, FileManagementType

class FileManagementSerializer(serializers.ModelSerializer):
    uploader = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FileManagement
        fields = "__all__"
        extra_kwargs = {
			'uploader': {'write_only': True}
		}


class FileManagementTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = FileManagementType
		fields = "__all__"
