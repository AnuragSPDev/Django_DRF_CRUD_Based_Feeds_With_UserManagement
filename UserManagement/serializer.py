from rest_framework import serializers
from .models import MyUser

class RegistrationSerilizer(serializers.ModelSerializer):
    '''
    Serializer for new user registration
    '''
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'date_of_birth', 'password']
        extra_kwargs = {'password': {'write_only':True}}

    def create(self, validated_data):
        user = MyUser(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            date_of_birth=validated_data.get('date_of_birth')
        )

        user.set_password(validated_data.get('password'))
        user.save()
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    '''
    Serializer for forgot password functionality
    '''
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    # defining create() as serializers.Serializer doesn't call create() method implicitly.
    def create(self, validated_data):
        user = MyUser()
        user.check_password(validated_data.get('old_password'))
        user.set_password(validated_data.get('new_password'))
        user.save()
        return user