from rest_framework import serializers
from planningandacquiring.models import K9
from profiles.models import User

class K9Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    capability = serializers.CharField(required=False)

    class Meta:
        model = K9
        fields = 'id', 'name', 'capability', 'handler'

   