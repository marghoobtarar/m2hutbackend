from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.encoding import force_text
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password','identityNumber',
                  "first_name", "gender", "city",
                  "last_name", "passport", "dob", 
                  "phone" , "cell" ,"address","zip_code",
                  "country", "trainingInstitute", "institutePhone",
                  "facilitatorName","institutionAccount", "instituteAddress",
                  "instituteCity", "instituteZip", "instituteCountry",
                  "registerName", "companyName", "accountStatus", 
                  "gender", "email_verified_at", "created_at", "updated_at",
                  "image",'admin_id','is_staff'
                    
                  ]

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        return user

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields =[
                  "first_name","gender", "city",'identityNumber',
                  "last_name", "passport", "dob", 
                  "phone" , "cell" ,"address"
                  ,"zip_code",
                  "country","image",
                  'accountStatus','is_active'
                #  "trainingInstitute", "institutePhone",
                #   "facilitatorName","institutionAccount", "instituteAddress",
                #   "instituteCity", "instituteZip", "instituteCountry",
                #   "registerName", "companyName", "accountStatus", 
                #   "gender", "email_verified_at", "updated_at",
                #   "image",'admin_id','is_staff','password'
                    
                  ]

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        return user

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_text(uid_decoder(attrs['uid']))
            self.user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'uid': ['Invalid value']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        return self.set_password_form.save()


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class EmailSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Invalid e-mail address'))

        return value
