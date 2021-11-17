from rest_framework.serializers import ModelSerializer
from humanoids.models import Humanoid

class HumanoidListSerializer(ModelSerializer):
    
    class Meta:
        model = Humanoid
        fields = ('id', 'name', 'surname', 'country', 'thumbnail_url')


class HumanoidDetailSerializer(ModelSerializer):

    class Meta:
        model = Humanoid
        fields = (
            'id', 
            'name', 
            'surname', 
            'address', 
            'bio', 
            'city', 
            'country',
            'email', 
            'mobile', 
            'phone', 
            'zip_code',
            'img_url'
        )