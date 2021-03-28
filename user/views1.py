from django.shortcuts import render
from django.db import connection

from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from adminside.serializer import LocationsSerializer, FeedbackRatingSerializer, PitStopSerializer, RecommendedLocationSerializer, CustomTokenObtainPairSerializer

from adminside.models import Locations, RatingFeedbackModel, PitStopModel, RecommendedLocationModal
from rest_framework import status, generics
from django.db.models import Sum, Count, Avg

from rest_framework_jwt.utils import jwt_decode_handler

from UserAuth.models import User

from django.http import HttpResponse
from django.conf import settings
import os
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from geopy.distance import geodesic
from collections import OrderedDict
from operator import itemgetter


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class FilterPitstopWithInRadius(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        payload = request.data
        In_range_pitstop = []

        try:

            pitstop = [PitStopSerializer(
                dat).data for dat in PitStopModel.objects.all()]

            currentLocation = (payload['latitude'],
                               payload['longitude'])
            for stop in pitstop:
                newLocation = (stop['latitude'],
                               stop['longitude'])
                distance = geodesic(currentLocation, newLocation).miles
                if distance <= 50:

                    data = {}
                    data['id'] = stop['id']
                    data['name'] = stop['name']
                    data['distance'] = distance
                    data['coordinates'] = {
                        'longitude': stop['longitude'], 'latitude': stop['latitude']}
                    data['rating'] = stop['rating']
                    In_range_pitstop.append(data)

        except (KeyError, PitStopModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:

            newlist = sorted(In_range_pitstop, key=itemgetter(
                'distance'), reverse=True)
            return Response(newlist, status=status.HTTP_200_OK)


class FilterPitstopWithGivenDestination(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        payload = request.data
        In_range_pitstop = []
        try:
            up = False
            down = False
            if (payload['longitude'] < payload['destination_longitude']):
                up = True
            if (payload['latitude'] < payload['destination_latitude']):
                down = True

            pitstop = [PitStopSerializer(
                dat).data for dat in PitStopModel.objects.all()]

            currentLocation = (
                payload['longitude'], payload['latitude'])
            destinationLocation = (
                payload['destination_longitude'], payload['destination_latitude'])
            distanceBetween = geodesic(
                currentLocation, destinationLocation).miles

            x_greater = payload['destination_latitude']
            x_smaller = payload['latitude']
            y_greater = payload['destination_longitude']
            y_smaller = payload['longitude']
            if payload['latitude'] >= payload['destination_latitude']:
                x_greater = payload['latitude']
                x_smaller = payload['destination_latitude']
            if payload['longitude'] >= payload['destination_longitude']:
                y_greater = payload['longitude']
                y_smaller = payload['destination_longitude']

            In_range_pitstop = [PitStopSerializer(
                dat).data for dat in PitStopModel.objects.raw("SELECT * FROM adminside_pitstopmodel WHERE (latitude BETWEEN %s AND %s) AND (longitude BETWEEN %s AND %s)", (payload['latitude'], payload['destination_latitude'], payload['longitude'], payload['destination_longitude']))]

        except (KeyError, PitStopModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:

            # serializer = PitStopSerializer(pitstop)
            return Response(In_range_pitstop, status=status.HTTP_200_OK)


class FilterLocationWithGivenPitStop(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        payload = request.data
        if request.headers.get('Authorization'):

            token = request.headers.get('Authorization').split(' ')[1]
            decoded_payload = jwt_decode_handler(token)
            userId = decoded_payload['user_id']
            In_range_pitstop = []
            try:
                location_data = {}
                location = [LocationsSerializer(
                    dat).data for dat in Locations.objects.filter(pit_stop=pk, location_type='gas_petrol').order_by('-distance_stop')]

                userExist = [FeedbackRatingSerializer(
                    dat).data for dat in RatingFeedbackModel.objects.filter(user=userId)]

                completeData = []
                newData = {}
                i = 0
                j = 0
                for dat in location:
                    # expectedResult = [d for d in location if d['id'] in keyValList]
                    user = RatingFeedbackModel.objects.filter(
                        user=userId, location_id=dat['id']).exists()
                    if user:
                        location[i]['is_rated'] = user
                    else:
                        location[i]['is_rated'] = user

                    coordinates = {
                        'longitude': location[i]['longitude'], 'latitude': location[i]['latitude']}
                    location[i]['coordinates'] = coordinates
                    location[i].pop('longitude')
                    location[i].pop('latitude')

                    i = i+1
                location_data['gasPetrol'] = location

                location = [LocationsSerializer(
                    dat).data for dat in Locations.objects.filter(pit_stop=pk, location_type='bathroom').order_by('-distance_stop')]
                # change location data into annotated data coordinate:{longitute=242, latitute:232}

                userExist = [FeedbackRatingSerializer(
                    dat).data for dat in RatingFeedbackModel.objects.filter(user=userId)]

                completeData = []
                newData = {}
                i = 0
                j = 0
                for dat in location:
                    user = RatingFeedbackModel.objects.filter(
                        user=userId, location_id=dat['id']).exists()
                    if user:
                        location[i]['is_rated'] = user
                    else:
                        location[i]['is_rated'] = user

                    coordinates = {
                        'longitude': location[i]['longitude'], 'latitude': location[i]['latitude']}
                    location[i]['coordinates'] = coordinates
                    location[i].pop('longitude')
                    location[i].pop('latitude')

                    i = i+1
                location_data['bathroom'] = location

                location = [LocationsSerializer(
                    dat).data for dat in Locations.objects.filter(pit_stop=pk, location_type='resturant').order_by('-distance_stop')]
                # change location data into annotated data coordinate:{longitute=242, latitute:232}

                userExist = [FeedbackRatingSerializer(
                    dat).data for dat in RatingFeedbackModel.objects.filter(user=userId)]

                completeData = []
                newData = {}
                i = 0
                j = 0
                for dat in location:
                    user = RatingFeedbackModel.objects.filter(
                        user=userId, location_id=dat['id']).exists()
                    if user:
                        location[i]['is_rated'] = user
                    else:
                        location[i]['is_rated'] = user

                    coordinates = {
                        'longitude': location[i]['longitude'], 'latitude': location[i]['latitude']}
                    location[i]['coordinates'] = coordinates
                    location[i].pop('longitude')
                    location[i].pop('latitude')

                    i = i+1
                location_data['resturnt'] = location

            except (KeyError, Locations.DoesNotExist):
                return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
            else:

                # serializer = PitStopSerializer(pitstop)
                return Response(location_data, status=status.HTTP_200_OK)

        else:

            In_range_pitstop = []
            try:
                location_data = {}
                location = [LocationsSerializer(
                    dat).data for dat in Locations.objects.filter(pit_stop=pk, location_type='gas_petrol').order_by('-distance_stop')]

                completeData = []
                newData = {}
                i = 0
                j = 0
                for dat in location:

                    coordinates = {
                        'longitude': location[i]['longitude'], 'latitude': location[i]['latitude']}
                    location[i]['coordinates'] = coordinates
                    location[i].pop('longitude')
                    location[i].pop('latitude')

                    i = i+1
                location_data['gasPetrol'] = location

                location = [LocationsSerializer(
                    dat).data for dat in Locations.objects.filter(pit_stop=pk, location_type='bathroom').order_by('-distance_stop')]
                # change location data into annotated data coordinate:{longitute=242, latitute:232}

                completeData = []
                newData = {}
                i = 0
                j = 0
                for dat in location:

                    coordinates = {
                        'longitude': location[i]['longitude'], 'latitude': location[i]['latitude']}
                    location[i]['coordinates'] = coordinates
                    location[i].pop('longitude')
                    location[i].pop('latitude')

                    i = i+1
                location_data['bathroom'] = location

                location = [LocationsSerializer(
                    dat).data for dat in Locations.objects.filter(pit_stop=pk, location_type='resturant').order_by('-distance_stop')]
                # change location data into annotated data coordinate:{longitute=242, latitute:232}

                completeData = []
                newData = {}
                i = 0
                j = 0
                for dat in location:

                    coordinates = {
                        'longitude': location[i]['longitude'], 'latitude': location[i]['latitude']}
                    location[i]['coordinates'] = coordinates
                    location[i].pop('longitude')
                    location[i].pop('latitude')

                    i = i+1
                location_data['resturnt'] = location

            except (KeyError, Locations.DoesNotExist):
                return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
            else:

                return Response(location_data, status=status.HTTP_200_OK)


class FilterPitstopDistanceRatingLocation(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        payload = request.data
        In_range_pitstop = []

        try:
            if payload['distance_selector']:
                contract = PitStopModel.objects.get(
                    id=payload['current_pitstop'])
                current_pitStop = PitStopSerializer(contract).data

                pitstop = [PitStopSerializer(
                    dat).data for dat in PitStopModel.objects.all()]

                currentLocation = (
                    current_pitStop['longitude'], current_pitStop['latitude'])
                for stop in pitstop:
                    if stop['id'] != payload['current_pitstop']:
                        newLocation = (
                            stop['longitude'], stop['latitude'])
                        distance = geodesic(currentLocation, newLocation).miles
                        if distance < payload['distance']:
                            In_range_pitstop.append(stop)
            elif payload['rating_selector']:
                pitstop = [PitStopSerializer(
                    dat).data for dat in PitStopModel.objects.all()]

                for stop in pitstop:
                    if stop['rating'] >= payload['rating']:
                        In_range_pitstop.append(stop)

            elif payload['gaspetrol_rating_pitstop']:

                gasStop = [GasPetrolSerializer(
                    dat).data for dat in GasPetrolModel.objects.all()]
                gas_in_range = []

                for stop in gasStop:
                    if stop['pit_stop'] in gas_in_range:
                        continue
                    else:
                        gas_in_range.append(stop['pit_stop'])

                pitStop = [PitStopSerializer(
                    dat).data for dat in PitStopModel.objects.all()]
                for stop in pitStop:

                    if stop['id'] in gas_in_range and stop['rating'] >= payload['rating']:
                        In_range_pitstop.append(stop)

            elif payload['resturant_rating_pitstop']:
                bathStop = [ResturantSerializer(
                    dat).data for dat in ResturantModel.objects.all()]
                gas_in_range = []

                for stop in bathStop:

                    if stop['pit_stop'] in gas_in_range:
                        continue
                    else:
                        gas_in_range.append(stop['pit_stop'])

                pitStop = [PitStopSerializer(
                    dat).data for dat in PitStopModel.objects.all()]
                for stop in pitStop:

                    if stop['id'] in gas_in_range and stop['rating'] >= payload['rating']:
                        In_range_pitstop.append(stop)
            elif payload['bathroom_rating_pitstop']:
                bathStop = [BathroomSerializer(
                    dat).data for dat in BathroomModel.objects.all()]
                pitStop_list = []

                for stop in bathStop:

                    if stop['pit_stop'] in pitStop_list:
                        continue
                    else:
                        pitStop_list.append(stop['pit_stop'])

                pitStop = [PitStopSerializer(
                    dat).data for dat in PitStopModel.objects.all()]

                for stop in pitStop:

                    if stop['id'] in pitStop_list and stop['rating'] >= payload['rating']:
                        In_range_pitstop.append(stop)

        except (KeyError, PitStopModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:

            # serializer = PitStopSerializer(pitstop)

            return Response(In_range_pitstop, status=status.HTTP_200_OK)


class PitStop(generics.ListCreateAPIView):
    # permission_classes = (IsAuthenticated,)

    queryset = PitStopModel.objects.all()

    serializer_class = PitStopSerializer


class ManagePitStop(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            contract = PitStopModel.objects.get(id=pk)
        except (KeyError, PitStopModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = PitStopSerializer(contract)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):

        payload = request.data

        try:
            home = PitStopModel.objects.get(id=pk)
        except (KeyError, PitStopModel.DoesNotExist):

            serializer = PitStopSerializer(data=payload)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:

            serializer = PitStopSerializer(home, data=payload)

            if serializer.is_valid():
                serializer.save()

                parser_classes = (MultiPartParser, FormParser)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            home = PitStopModel.objects.get(id=pk)
        except (KeyError, PitStopModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            home.delete()
            deleteLocation(pk)
            return Response('Data deleted', status=status.HTTP_200_OK)
        # return Response('Data deleted', status=status.HTTP_200_OK)


class RecommendedLocation(APIView):

    def get(self, request):
        payload = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)
        data = [RecommendedLocationSerializer(
            da).data for da in RecommendedLocationModal.objects.all().select_related('user')]

        users = RecommendedLocationModal.objects.all().select_related("user")
        i = 0
        for e in users:
            data[i]['email'] = e.user.email

        return Response(data)

    def post(self, request):
        payload = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)
        try:
            user_data = User.objects.filter(id=decoded_payload['user_id'])

        except (KeyError, User.DoesNotExist):
            error = ''
            badrequest = {error: 'bad request error'}

            return Response({'bad request error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            payload['user'] = decoded_payload['user_id']
            payload['status'] = 1
            serializer = RecommendedLocationSerializer(data=payload)
            if serializer.is_valid():
                instance = serializer.save()
                instance.save()
            return Response({"response": "successfully recommended"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageRecommendedLocation(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = (IsAuthenticated,)

    queryset = RecommendedLocationModal.objects.all()

    serializer_class = RecommendedLocationSerializer


class FeedbackRating(APIView):

    def get(self, request):
        payload = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)
        return Response([FeedbackRatingSerializer(da).data for da in RatingFeedbackModel.objects.filter(user=decoded_payload['user_id'])])

    def post(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)

        payload = request.data

        payload['user'] = decoded_payload['user_id']

        serializer = FeedbackRatingSerializer(data=payload)

        try:
            pitstop = PitStopModel.objects.get(id=payload['pit_stop_id'])

        except (KeyError, PitStopModel.DoesNotExist):
            error = ''
            badrequest = {error: 'bad request error'}

            return Response({'bad request error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if serializer.is_valid():
                instance = serializer.save()
                instance.save()

                totalRating = RatingFeedbackModel.objects.filter(
                    location_id=payload['location_id']).aggregate(rating=Avg('rating'))

                pitData = Locations.objects.filter(
                    id=payload['location_id']).update(rating_stop=totalRating['rating'])

                putData(payload['pit_stop_id'])

                return Response({"response": "successfully rated"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def putData(stopId):

    try:
        pitstop = PitStopModel.objects.get(id=stopId)
    except (KeyError, PitStopModel.DoesNotExist):
        error = ''
        badrequest = {error: 'bad request error'}

        return Response({error: 'bad request error'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        rest = Locations.objects.filter(
            pit_stop=stopId, rating_stop__gt=0, location_type='resturant').aggregate(rating=Avg('rating_stop'))
        bath = Locations.objects.filter(
            pit_stop=stopId,  rating_stop__gt=0, location_type='bathroom').aggregate(rating=Avg('rating_stop'))
        gasPetrol = Locations.objects.filter(
            pit_stop=stopId, rating_stop__gt=0,  location_type='gas_petrol').aggregate(rating=Avg('rating_stop'))

        increment = 0
        totalRating = 0
        if rest['rating'] != None and rest['rating'] != 0:
            increment += 1
            totalRating = totalRating + rest['rating']

        if bath['rating'] != None and bath['rating'] != 0:
            increment += 1
            totalRating = totalRating + bath['rating']

        if gasPetrol['rating'] != None and gasPetrol['rating'] != 0:
            increment += 1
            totalRating = totalRating + gasPetrol['rating']

            totalRating = round(float(totalRating/increment), 2)

        PitStopModel.objects.filter(
            id=stopId).update(rating=totalRating)


def deleteLocation(pk):

    gas_petrols = [GasPetrolSerializer(
        dat).data for dat in GasPetrolModel.objects.all()]
    for gas_petrol in gas_petrols:
        if(gas_petrol['pit_stop'] == pk):
            home = GasPetrolModel.objects.get(id=gas_petrol['id'])
            home.delete()
    rests = [ResturantSerializer(
        dat).data for dat in ResturantModel.objects.all()]
    for rest in rests:
        if(rest['pit_stop'] == pk):
            home = ResturantModel.objects.get(id=rest['id'])
            home.delete()
    baths = [BathroomSerializer(
        dat).data for dat in BathroomModel.objects.all()]

    for bath in baths:
        if(bath['pit_stop'] == pk):
            home = BathroomModel.objects.get(id=bath['id'])
            home.delete()
    return 1
