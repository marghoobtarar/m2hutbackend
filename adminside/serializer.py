from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# user model
from django.contrib.auth.models import User

# other models
from .models import (WorkLogsModel,
                    WorkLogsDetailsModel, 
                    WorkLogsBreakModel,
                    NoticesModel,
                    StyleModel,
                    TypographyModel,
                    RegisterEmailModel,
                    SuspensionEmailModel,
                    AdminEmailModel,
                    )

# from .models import

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        attrs['email'] = attrs['email'].lower()
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        data['message']="user authenticated successfully"
        data['access_token'] = data['access']
        data.pop('refresh')
        data.pop('access')
        data['user']= {}
        data['user']['id']=self.user.id
        data['user']['admin_id']=self.user.admin_id_id
        data['user']['email']=self.user.email
        data['user']['first_name']=self.user.first_name
        data['user']['last_name']=self.user.last_name
        data['user']['companyName']=self.user.companyName
        data['user']['registerName']=self.user.registerName
        data['user']['is_staff']=self.user.is_staff

        if self.user.image is not None:
            data['user']['image']= "media/"+str(self.user.image)
        else:
            data['user']['image']=None

        return data

# work log serilizer

class WorkLogSerilizer(serializers.ModelSerializer):
    class Meta:
        model = WorkLogsModel
        fields = ('id', 'user_id',
                   'created_at',
                   'end_at',
                   'total_works_hours',
                   'total_break_time'
                   )
    
    def create( self, validated_data):
        worklog = WorkLogsModel.objects.create(**validated_data)
        return worklog
    
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance
class WorkLogDetailsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = WorkLogsDetailsModel
        fields = ('id', 'worklog_id',
                   'address','captured_image',
                   'latitude','longitude',
                   'work_log_break_id',
                   'worklog_type',
                   'created_at'
                   )
    
    def create( self, validated_data):
        worklog = WorkLogsDetailsModel.objects.create(**validated_data)
        return worklog
    
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

class WorkLogsBreakSerilizer(serializers.ModelSerializer):
    class Meta:
        model = WorkLogsBreakModel
        fields = '__all__'
    
    def create(self, validated_data):
        breakLogs = WorkLogsBreakModel.objects.create(**validated_data)
        return breakLogs
    
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

class NoticesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticesModel
        fields = ('id', 'created_at',
                   'updated_at',
                   'description',
                   'heading',
                   'publish',
                   'draft',
                   'image',
                   'author',
                   'admin_id',
                   'date'

                   )
    
    def create( self, validated_data):
        notices = NoticesModel.objects.create(**validated_data)
        return notices
    
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StyleModel
        fields = '__all__'
    def create(self, validated_data):
        style = StyleModel.objects.create(**validated_data)
        return style
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

class TypographySerializer(serializers.ModelSerializer):
    class Meta:
        model = TypographyModel
        fields = '__all__'
    def create(self, validated_data):
        style = TypographyModel.objects.create(**validated_data)
        return style
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

class RegisterEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterEmailModel
        fields = '__all__'
    def create(self, validated_data):
        style = RegisterEmailModel.objects.create(**validated_data)
        return style
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

class SuspensionEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspensionEmailModel
        fields = '__all__'
    def create(self, validated_data):
        style = SuspensionEmailModel.objects.create(**validated_data)
        return style
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance
class AdminEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminEmailModel
        fields = '__all__'
    def create(self, validated_data):
        style = AdminEmailModel.objects.create(**validated_data)
        return style
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance

