from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, ReadOnlyField
from django.contrib.auth.models import User

from .models import Locations,  PitStopModel, RecommendedLocationModal, RatingFeedbackModel, RecommendedPositionModal, RecommendedPositionLocationModal

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        print(attrs)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        print('testing 123',self.user)
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
        if self.user.image:
            data['user']['image']=self.user.image
        else:
            data['user']['image']=None



        return data


class PitStopSerializer(serializers.ModelSerializer):

    class Meta:
        model = PitStopModel

        # fields = ['id', 'name', 'longitude', 'latitude', 'rating']
        fields = '__all__'

    def create(self, validated_data):
        driverprofile = PitStopModel.objects.create(**validated_data)
        return driverprofile

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance


class LocationsSerializer(serializers.ModelSerializer):
    # pit_stop = PitStopSerializer(many=False)

    class Meta:
        model = Locations
        fields = ['id', 'name','pit_stops',
                  'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type','city']
        # fields = '__all__'

    def create(self, validated_data):
        driverprofile = Locations.objects.create(**validated_data)
        return driverprofile

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance



class RecommendedLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecommendedLocationModal
        fields = ['id', 'user', 'gener', 'message', 'status']

    def create(self, validated_data):
        driverprofile = RecommendedLocationModal.objects.create(
            **validated_data)
        return driverprofile

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance


class RecommendedPositionSerilizer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedPositionModal
        fields = '__all__'
        # fields = ['name', 'latitude', 'longitude', 'status']

    def create(self, validated_data):
        instance = RecommendedPositionModal.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance


class RecommendedPositionLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedPositionLocationModal
        fields = '__all__'

    def create(self, validated_data):
        # print(instance)

        instance = RecommendedPositionLocationModal.objects.create(
            **validated_data)
        return instance

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance


# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = UserModel
#         # fields = '__all__'

#         fields = ['id', 'name', 'email', 'phone', 'city', 'address', 'image']

#     def create(self, validated_data):
#         driverprofile = UserModel.objects.create(**validated_data)
#         return driverprofile

#     def update(self, instance, validated_data):
#         for k, v in validated_data.items():
#             setattr(instance, k, v)
#             instance.save()
#         return instance


class FeedbackRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = RatingFeedbackModel
        fields = ['id', 'user', 'feedback', 'rating',
                  'location_id', 'pit_stop_id']

    def create(self, validated_data):
        driverprofile = RatingFeedbackModel.objects.create(**validated_data)
        return driverprofile

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
            instance.save()
        return instance
