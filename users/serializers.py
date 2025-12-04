
# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import LibraryUser

class LibraryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryUser
        fields = ['id', 'name', 'last_name', 'school_mail', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_school_mail(self, value):
        if LibraryUser.objects.filter(school_mail=value).exists():
            raise serializers.ValidationError('Bu mail zaten kayıtlı!')
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
