from rest_framework import serializers
from unitmanagement.models import Notification
from django.contrib.auth.models import User

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = 'id', 'k9', 'user', 'position', 'message', 'viewed', 'datetime'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id','username', 'password'