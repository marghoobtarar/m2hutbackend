from django.shortcuts import render
import requests
import json
from math import isinf, sin, cos, sqrt, atan2, radians
from django.http import QueryDict

from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializer import  LocationsSerializer, PitStopSerializer,  RecommendedLocationSerializer, RecommendedPositionSerilizer, RecommendedPositionLocationSerializer
from .models import Locations, PitStopModel,  RecommendedLocationModal, RecommendedPositionModal, RecommendedPositionLocationModal
from rest_framework import status, generics

from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework_jwt.utils import jwt_decode_handler

from django.http import HttpResponse
from django.conf import settings
import os
from django.db.models import Q
from geopy.distance import geodesic
import math
from .city_state import get_city_state


class FrontendAppView(APIView):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, request):
        try:
            with open(os.path.join(settings.REACT_APP_DIR, 'build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            logging.exception('Production build of app not found')
            return HttpResponse(
                """
                    This URL is only used when you have built the production
                    version of the app. Visit http://localhost:3000/ instead, or
                    run `yarn run build` to test the production version.
                    """,
                status=501,
            )


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        content = {'message': 'Hello, World!'}
        return Response(content)


class PitStop(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):

        # token = request.headers.get('Authorization').split(' ')[1]
        # decoded_payload = jwt_decode_handler(token)
        pitstop = [PitStopSerializer(
            da).data for da in PitStopModel.objects.all()[0:500]]
        count = PitStopModel.objects.count()
        # print(pitstop)
        # print('data getting zero')
        for i in range(0, len(pitstop)):

            pitstop[i]['tId'] = i+1
        # print('data getting one')
        data = {}
        data['data'] = pitstop
        data['count'] = count

        return Response(data)

    def post(self, request):
        payload = request.data
        print(payload)
        st = location(payload)
        if(int(st) == 201):

            return Response(status=status.HTTP_201_CREATED)
        elif(int(st) == 209):
            return Response(status=status.HTTP_409_CONFLICT)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PitStopAll(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):

        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)
        pitstop = [PitStopSerializer(
            da).data for da in PitStopModel.objects.all()]
        # print('data getting zero')
        for i in range(0, len(pitstop)):
            pitstop[i]['tId'] = i+1

        return Response(pitstop)


class PitStopSearch(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        payload = request.data
        if(payload['text'] != ''):
            pitstop = [PitStopSerializer(
                da).data for da in PitStopModel.objects.filter(Q(name__icontains=payload['text']) | Q(longitude__icontains=payload['text']) | Q(latitude__icontains=payload['text']) | Q(rating__icontains=payload['text']))]
        else:
            pitstop = [PitStopSerializer(
                da).data for da in PitStopModel.objects.filter(Q(name__icontains=payload['text']) | Q(longitude__icontains=payload['text']) | Q(latitude__icontains=payload['text']) | Q(rating__icontains=payload['text']))[0:500]]

        # print('data getting zero')
        # print(pitstop)
        for i in range(0, len(pitstop)):
            pitstop[i]['tId'] = i+1

        return Response(pitstop)


class PitStopList(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        # print(request.data)
        pitstop = [PitStopSerializer(
            da).data for da in PitStopModel.objects.all()[request.data['start']:request.data['limit']]]
        # count = PitStopModel.objects.count()
        # print('data getting zero')
        for i in range(0, len(pitstop)):
            pitstop[i]['tId'] = request.data['start']
            request.data['start'] = request.data['start'] + 1
        # print('data getting one')
        # data = {}
        # data['data'] = pitstop
        # data['count'] = count

        return Response(pitstop)


class FilePitStop(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):

        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)
        data = [PitStopSerializer(
            da).data for da in PitStopModel.objects.all()]
        for i in range(0, len(data)):
            data[i]['tId'] = i+1

        return Response(data)

    def post(self, request):
        # st = location(request)
        payload = request.data['file'][1:]
        st = 0
        i = 0
        for dat in payload:
            newData = {}
            # print(dat)

            try:

                newData['name'] = dat[0]

                latLang = dat[2].split(",")
                newData['latitude'] = float(latLang[0])
                newData['longitude'] = float(latLang[1])

            except:
                # print('the error is occuring on the array index', i)
                i = i+1
            else:
                st = location(newData)
                # print('it has been added')
                i = i+1

        if(int(st) == 201):

            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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

            location(request)
            return Response(status=status.HTTP_201_CREATED)

        else:
            # print(' the request data is here', request)
            if payload['nameChange']:
                payloadD = {}
                payloadD['name'] = payload['name']
                payloadD['latitude'] = payload['latitude']
                payloadD['longitude'] = payload['longitude']
                payloadD['rating'] = payload['rating']
                payloadD['id'] = payload['id'],
                payloadD['city'] = payload['city']

                # print('name will be updated')

                serializer = PitStopSerializer(home, data=payloadD)

                if serializer.is_valid():
                    serializer.save()
                    # print('name has been updated')
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    print('name is not updated')
                    return Response(status=status.HTTP_201_CREATED)

            else:
                # print('the data is', payload)
                # print('changing all of the data')
                home.delete()
                st = location(payload)
                # st = 201
                if(int(st) == 201):

                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            home = PitStopModel.objects.get(id=pk)
        except (KeyError, PitStopModel.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            home.delete()
            return Response('Data deleted', status=status.HTTP_200_OK)


class LocationSearch(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        payload = request.data
        data = {}

        # print('filter data', location)
            # location = [LocationsSerializer(
            #     da).data for da in Locations.objects.filter(Q(name__icontains=payload['text']) | Q(pit_stop__name__icontains=payload['text']) | Q(longitude__icontains=payload['text']) | Q(latitude__icontains=payload['text']) | Q(distance_stop__icontains=payload['text']) | Q(rating_stop__icontains=payload['text']))]
            # print(location)
        resturant = Locations.objects.values('id', 'pit_stop__name', 'name',
                                                'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type').filter(Q(name__icontains=payload['text']) | Q(pit_stop__name__icontains=payload['text']) | Q(longitude__icontains=payload['text']) | Q(latitude__icontains=payload['text']) | Q(distance_stop__icontains=payload['text']) | Q(rating_stop__icontains=payload['text'])).filter(location_type='resturant')
        bathroom = Locations.objects.values('id', 'pit_stop__name', 'name',
                                                'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type').filter(Q(name__icontains=payload['text']) | Q(pit_stop__name__icontains=payload['text']) | Q(longitude__icontains=payload['text']) | Q(latitude__icontains=payload['text']) | Q(distance_stop__icontains=payload['text']) | Q(rating_stop__icontains=payload['text'])).filter(location_type='bathroom')
        gas_petrol = Locations.objects.values('id', 'pit_stop__name', 'name',
                                                'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type').filter(Q(name__icontains=payload['text']) | Q(pit_stop__name__icontains=payload['text']) | Q(longitude__icontains=payload['text']) | Q(latitude__icontains=payload['text']) | Q(distance_stop__icontains=payload['text']) | Q(rating_stop__icontains=payload['text'])).filter(location_type='gas_petrol')
        data={'resturant':resturant,'bathroom':bathroom,'gas_petrol':gas_petrol}
       

       
        # for i in range(0, len(location)):
        #     location[i]['tId'] = i+1
        #     # print(dict(location[i]['pit_stop']))
        #     location[i]['pit_stop'] = location[i]['pit_stop__name']

        # print(location)
        return Response(data)


def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n


class Location(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):

        resturant = Locations.objects.values('id','pit_stop__name','name',
                                            'longitude' ,'latitude', 'distance_stop', 'rating_stop', 'location_type','city').filter(location_type='resturant')[0:500]
        bathroom = Locations.objects.values('id', 'pit_stop__name', 'name',
                                            'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type','city').filter(location_type="bathroom")[0:500]
        gas_petrol = Locations.objects.values('id', 'pit_stop__name', 'name',
                                            'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type','city').filter(location_type="gas_petrol")[0:500]

     
        
        count = {}
        count['resturant'] = Locations.objects.filter(
            location_type='resturant').count()
        count['bathroom'] = Locations.objects.filter(
            location_type='bathroom').count()
        count['gas_petrol'] = Locations.objects.filter(
            location_type='gas_petrol').count()
        print(resturant)

        if(len(resturant) == len(bathroom) and len(resturant)==len(gas_petrol)):
            for i in range(0, len(resturant)):
                resturant[i]['idk'] = i+1
                bathroom[i]['idk'] = i+1
                gas_petrol[i]['idk'] = i+1
                
        else:
            for i in range(0, len(resturant)):
                resturant[i]['idk'] = i+1
            for i in range(0, len(bathroom)):
                bathroom[i]['idk'] = i+1
            for i in range(0, len(gas_petrol)):
                gas_petrol[i]['idk'] = i+1
                
     
        


        
           

        # print('data getting one')
        
        data = {}
        data['data'] = {'resturant':resturant,'bathroom':bathroom,'gas_petrol':gas_petrol}
        data['count'] = count
        print(count)
        # print(data)

        return Response(data)

    def post(self, request):

        payload = request.data
        latitudeGet = float(truncate(payload['location']['latitude'], 1))
        longitudeGet = float(truncate(payload['location']['longitude'], 1))

        data = [PitStopSerializer(dat).data for dat in PitStopModel.objects.filter(
            latitude__gte=latitudeGet, longitude__gte=longitudeGet, latitude__lte=latitudeGet+.1, longitude__lte=longitudeGet+.1
        )]
        newLocation = (payload['location']['latitude'],
                       payload['location']['longitude'])

        for el in data:

            currentLocation = (el['latitude'],
                               el['longitude'])

            distance = geodesic(currentLocation, newLocation).miles
            pitstopis = PitStopModel.objects.filter(
                longitude=el['longitude'], latitude=el['latitude']).first()
            if(not Locations.objects.filter(longitude=payload['location']['longitude'], latitude=payload['location']['latitude']).exists() and distance <= 2):
                payload['location']['distance_stop'] = distance

                serializer = LocationsSerializer(data=payload['location'])
                if serializer.is_valid():
                    instance = serializer.save()
                    instance.save()
                    print('add new location')
                    instance.pit_stop.add(pitstopis)
                    print('pitstop added')
                else:
                    print('it is bad request')
                    # return Response(status=HTTP_400_BAD_REQUEST)
            else:

                pre_location = Locations.objects.filter(
                    longitude=payload['location']['longitude'], latitude=payload['location']['latitude']).first()
                print('added in already locaitno', pitstopis)
                pre_location.pit_stop.add(pitstopis)
                # return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_201_CREATED)


class LocationList(APIView):

    def post(self, request):
        
        location = Locations.objects.values('id', 'pit_stop__name', 'name',
                                            'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type','city').filter(location_type=request.data['location'])[request.data['start']:request.data['start']+500]

        j = request.data['start']
        for i in range(0, len(location)):
            location[i]['idk'] = j
            j+=1

        return Response(location)


# class ManageLocation(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = (IsAuthenticated,)
#     queryset = Locations.objects.all()
#     serializer_class = LocationsSerializer


class ManageLocation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            contract = Locations.objects.get(id=pk)
        except (KeyError, Locations.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = LocationsSerializer(contract)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):

        payload = request.data
        # print('the new data is', payload)

        try:
            home = Locations.objects.get(id=pk)
            new = Locations.objects.values('id', 'pit_stop', 'name',
                                           'longitude', 'latitude', 'distance_stop', 'rating_stop', 'location_type').get(id=pk)

        except (KeyError, Locations.DoesNotExist):

            # serializer = LocationsSerializer(data=payload)

            # if serializer.is_valid():
            #     serializer.save()
            # else:
            #     print('serilizer is not working')

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            new['name'] = payload['name']
            new['longitude'] = payload['longitude']
            new['latitude'] = payload['latitude']
            new['rating_stop'] = payload['rating_stop']
            new['city'] = payload['city']

            serializer = LocationsSerializer(home, data=new)
            # print(new)

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print('serilizer is not true')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            home = Locations.objects.get(id=pk)
        except (KeyError, Locatinos.DoesNotExist):
            return Response('Data not found', status=status.HTTP_404_NOT_FOUND)
        else:
            home.delete()
            return Response('Data deleted', status=status.HTTP_200_OK)
        return Response('Data deleted', status=status.HTTP_200_OK)


class RecommendedLocation(APIView):

    def get(self, request, pk):
        try:
            data = RecommendedLocationModal.objects.values(
                'id', 'gener', 'user__email', 'message', 'status').filter(status=pk)
        except (KeyError, RecommendedLocationModal.DoesNotExist):
            error = ''
            badrequest = {error: 'bad request error'}
        else:
            gener = [RecommendedLocationSerializer(
                dat).data for dat in RecommendedLocationModal.objects.values('gener').distinct()]
            array = [x['gener'] for x in gener]
        return Response({'data': data, 'gener': array})

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
            payload['status'] = 0
            serializer = RecommendedLocationSerializer(data=payload)
            if serializer.is_valid():
                instance = serializer.save()
                instance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageRecommendedLocation(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = RecommendedLocationModal.objects.all()

    serializer_class = RecommendedLocationSerializer


class RecommendedPosition(APIView):
    def get(self, request, pk):

        try:
            data = [RecommendedPositionSerilizer(
                dat).data for dat in RecommendedPositionModal.objects.filter(status=pk)]
        except (KeyError, RecommendedPositionModal.DoesNotExist):
            error = ''
            badrequest = {error: 'bad request error'}

            return Response({'bad request error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data)


class ManageRecommendedPosition(generics.RetrieveUpdateDestroyAPIView):
    queryset = RecommendedPositionModal.objects.all()
    serializer_class = RecommendedPositionSerilizer


class RecommendedPositionLocation(APIView):
    def get(self, request, pk):

        try:
            data = [RecommendedPositionLocationSerializer(
                dat).data for dat in RecommendedPositionLocationModal.objects.filter(status=pk)]
        except (KeyError, RecommendedPositionLocationModal.DoesNotExist):
            error = ''
            badrequest = {error: 'bad request error'}

            return Response({'bad request error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data)

    def post(self, request):
        payload = request.data
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_payload = jwt_decode_handler(token)
        try:
            user_data = User.objects.filter(
                id=decoded_payload['user_id']).exists()
        except(KeyError, User.DoesNotExist):

            return Response({'bad request error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            payload['user'] = decoded_payload['user_id']
            payload['status'] = 1

            serializer = RecommendedPositionLocationSerializer(data=payload)
            if serializer.is_valid():
                instance = serializer.save()
                instance.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageRecommendedPositionLocation(generics.RetrieveUpdateDestroyAPIView):
    queryset = RecommendedPositionLocationModal.objects.all()
    serializer_class = RecommendedPositionLocationSerializer


def putData(stopId):

    try:
        pitstop = PitStopModel.objects.get(id=stopId)
    except (KeyError, PitStopModel.DoesNotExist):

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:

        resturants = [ResturantSerializer(
            dat).data for dat in ResturantModel.objects.all()]
        bath_rest_gas = 0
        resturntRating = 0
        totalRest = 0
        for resturant in resturants:
            if(resturant['pit_stop'] == stopId):
                resturntRating += resturant['rating_stop']
                totalRest += 1

        if totalRest != 0:
            resturntRating = (resturntRating/totalRest)
            bath_rest_gas += 1

        bathrooms = [BathroomSerializer(
            dat).data for dat in BathroomModel.objects.all()]

        bathroomRating = 0
        totalBath = 0
        for bathroom in bathrooms:
            if(bathroom['pit_stop'] == stopId):
                bathroomRating += bathroom['rating_stop']
                totalBath += 1
        if totalBath != 0:
            bathroomRating = bathroomRating/totalBath
            bath_rest_gas += 1

        gas_petrols = [GasPetrolSerializer(
            dat).data for dat in GasPetrolModel.objects.all()]

        gas_petrolRating = 0
        totalPet = 0
        for gas_petrol in gas_petrols:
            if(gas_petrol['pit_stop'] == stopId):
                gas_petrolRating += gas_petrol['rating_stop']

                totalPet += 1
        if totalPet != 0:
            gas_petrolRating = gas_petrolRating/totalPet
            bath_rest_gas += 1
        totalRating = 0
        if bath_rest_gas != 0:
            totalRating = (
                resturntRating+gas_petrolRating+bathroomRating)/bath_rest_gas

        singlePitdata = {}
        pitstoplist = [PitStopSerializer
                       (dat).data for dat in PitStopModel.objects.all()]

        for elemtent in pitstoplist:
            if(elemtent['id'] == stopId):
                singlePitdata = elemtent
        singlePitdata['rating'] = totalRating

        serializerPit = PitStopSerializer(pitstop, data=singlePitdata)
        if serializerPit.is_valid():
            serializerPit.save()
            parser_classes = (MultiPartParser, FormParser)

            return Response(serializerPit.data, status=status.HTTP_201_CREATED)
        return Response(serializerPit.errors, status=status.HTTP_400_BAD_REQUEST)


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


def GetDistance(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance*0.621371


def location(request):
    # radius = 3000
    payload = request
    lati = float(payload['latitude'])
    longi = float(payload['longitude'])
    city = get_city_state(lati,longi)
    payload['city'] = city
    # print(lati, longi)
    isExist = PitStopModel.objects.filter(
        latitude=payload['latitude'], longitude=payload['longitude']).exists()
    # print('checking if exists',isExist)
    if (not isExist):
        print('entering new data')
        serializer = PitStopSerializer(data=payload)
        pitStopId = 0
        print('check serilizer')
        if serializer.is_valid():
            instance = serializer.save()
            instance.save()
            pitStopId = serializer.data['id']
            pitstopis = instance
            # print('it has saved')

            radius = 1609
            data_dict = {"food": [], "gas_station": [], "bathroom": []}
            next_token_flag = False

            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lati)+','+str(longi)+'&radius='+str(
                radius)+'&type=restaurant&hasNextPage=true&nextPage()=true&sensor=false&key=AIzaSyA22SLyxLFLzz0Nb2MjG77ORmbi2jrJGJk'

            r = requests.get(url)
            content = []
            content.append(r.text)
            next_token = ""
            for i in content:
                loc = json.loads(i)
                if 'next_page_token' in loc:
                    next_token_flag = True
                    next_token = loc['next_page_token']
                try:
                    for item in loc['results']:
                        try:
                            data_dict['food'].append({
                                "name": item['name'],
                                "coordinates": {"longitude": item["geometry"]["location"]["lng"], "latitude": item["geometry"]["location"]["lat"]},
                                # "ratings": item["rating"],
                                "distance": float(GetDistance(lati, longi, item["geometry"]["location"]["lat"], item["geometry"]["location"]["lng"]))

                            })
                            # print('food data is', data_dict['food'])
                        except:
                            pass
                except:
                    pass

            import time
            time.sleep(2)
            while next_token_flag:
                url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=' + \
                    str(next_token)+'&key=AIzaSyA22SLyxLFLzz0Nb2MjG77ORmbi2jrJGJk'
                r = requests.get(url)
                content = []
                content.append(r.text)
                for i in content:
                    loc = json.loads(i)
                    if 'next_page_token' in loc:
                        next_token_flag = True
                        next_token = loc['next_page_token']
                    else:
                        next_token_flag = False

                    try:
                        for item in loc['results']:
                            try:
                                data_dict['food'].append({
                                    "name": item['name'],
                                    "coordinates": {"longitude": item["geometry"]["location"]["lng"], "latitude": item["geometry"]["location"]["lat"]},
                                    # "ratings": item["rating"],
                                    "distance": float(GetDistance(lati, longi, item["geometry"]["location"]["lat"], item["geometry"]["location"]["lng"]))

                                })
                                # print('while ', data_dict['food'])

                            except:
                                pass
                    except:
                        pass

            time.sleep(2)

            next_token_flag = False
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lati)+','+str(longi)+'&radius='+str(
                radius)+'&type=gas_station&hasNextPage=true&nextPage()=true&sensor=false&key=AIzaSyA22SLyxLFLzz0Nb2MjG77ORmbi2jrJGJk'
            r = requests.get(url)
            content = []
            content.append(r.text)
            next_token = ""
            for i in content:
                loc = json.loads(i)
                if 'next_page_token' in loc:
                    next_token_flag = True
                    next_token = loc['next_page_token']
                try:
                    for item in loc['results']:
                        try:

                            data_dict['gas_station'].append({
                                "name": item['name'],
                                "coordinates": {"longitude": item["geometry"]["location"]["lng"], "latitude": item["geometry"]["location"]["lat"]},
                                "distance": float(GetDistance(lati, longi, item["geometry"]["location"]["lat"], item["geometry"]["location"]["lng"]))

                            })
                            # print('shwing gas_station', item)

                        except:
                            pass
                except:
                    pass

            import time
            time.sleep(2)
            while next_token_flag:
                url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=' + \
                    str(next_token)+'&key=AIzaSyA22SLyxLFLzz0Nb2MjG77ORmbi2jrJGJk'
                r = requests.get(url)
                content = []
                content.append(r.text)
                for i in content:
                    loc = json.loads(i)
                    if 'next_page_token' in loc:
                        next_token_flag = True
                        next_token = loc['next_page_token']
                    else:
                        next_token_flag = False

                    try:
                        for item in loc['results']:
                            try:
                                data_dict['gas_station'].append({
                                    "name": item['name'],
                                    "coordinates": {"longitude": item["geometry"]["location"]["lng"], "latitude": item["geometry"]["location"]["lat"]},
                                    # "ratings": item["rating"],
                                    "distance": float(GetDistance(lati, longi, item["geometry"]["location"]["lat"], item["geometry"]["location"]["lng"]))

                                })
                                # print('while shwing gas_station', item)

                            except:
                                pass
                    except:
                        pass

            time.sleep(2)

            next_token_flag = False
            url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?location='+str(lati)+','+str(longi)+'&radius='+str(
                radius)+'&query=toilet&hasNextPage=true&nextPage()=true&sensor=false&key=AIzaSyA22SLyxLFLzz0Nb2MjG77ORmbi2jrJGJk'
            r = requests.get(url)
            content = []
            content.append(r.text)
            next_token = ""
            for i in content:
                loc = json.loads(i)
                if 'next_page_token' in loc:
                    next_token_flag = True
                    next_token = loc['next_page_token']
                try:
                    for item in loc['results']:
                        try:
                            distance = float(GetDistance(
                                lati, longi, item["geometry"]["location"]["lat"], item["geometry"]["location"]["lng"]))
                            if distance < 1:
                                data_dict['bathroom'].append({
                                    "name": item['name'],
                                    "coordinates": {"longitude": item["geometry"]["location"]["lng"], "latitude": item["geometry"]["location"]["lat"]},
                                    # "ratings": item["rating"],
                                    "distance": distance

                                })
                                # print('bathroom', item)

                        except:
                            pass

                except:
                    pass

            import time
            time.sleep(2)
            while next_token_flag:
                url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken=' + \
                    str(next_token)+'&key=AIzaSyA22SLyxLFLzz0Nb2MjG77ORmbi2jrJGJk'
                r = requests.get(url)
                content = []
                content.append(r.text)
                for i in content:
                    loc = json.loads(i)
                    if 'next_page_token' in loc:
                        next_token_flag = True
                        next_token = loc['next_page_token']
                    else:
                        next_token_flag = False

                    try:
                        for item in loc['results']:
                            try:
                                distance = float(GetDistance(
                                    lati, longi, item["geometry"]["location"]["lat"], item["geometry"]["location"]["lng"]))
                                if distance < 1:
                                    data_dict['bathroom'].append({
                                        "name": item['name'],
                                        "coordinates": {"longitude": item["geometry"]["location"]["lng"], "latitude": item["geometry"]["location"]["lat"]},
                                        # "ratings": item["rating"],
                                        "distance": distance

                                    })
                                    # print('while bathroom', data_dict)
                            except:
                                pass
                    except:
                        pass
                # print(data_dict)
                time.sleep(2)
            resturants = data_dict['food']

            # newData = {}

            insert_location(resturants, 'resturant', pitstopis)

          
            gasStations = data_dict['gas_station']
            insert_location(gasStations, 'gas_petrol', pitstopis)

            
            bathrooms = data_dict['gas_station']
            insert_location(bathrooms, 'bathroom', pitstopis)

            
            bathrooms = data_dict['bathroom']
            insert_location(bathrooms, 'bathroom', pitstopis)

            
            return status.HTTP_201_CREATED
        else:
            print('wrong serilizer')
            return Response('wrong serilizer')
    else:

        return status.HTTP_409_CONFLICT
    # return status.HTTP_400_BAD_REQUEST

class resolveMigration(APIView):
    def post(self,request):
        dat =  Locations.objects.all()  
        for location in dat:

            data = LocationsSerializer(location).data
            pre_location = Locations.objects.get(id = data['id'])
            
            pre_location.pit_stops.add(data['pit_stop'])
            pre_location.save()
            data = LocationsSerializer(pre_location).data
            print(data)
           
        return Response(status=status.HTTP_201_CREATED)

def insert_location(location, location_type, pitstopis):
    newData = {}
    # print('adding resturant through function')

    for resturant in location:
        # coordinate = resturant['coordinates']
        newData['longitude'] = resturant['coordinates']['longitude']
        newData['latitude'] = resturant['coordinates']['latitude']
        # newData['pit_stop'] = pitstopis
        # print()
        
        isExist = Locations.objects.filter(
            longitude=newData['longitude'], latitude=newData['latitude']).exists()
        if(not isExist):

            newData['name'] = resturant['name']

            newData['rating_stop'] = 0
            newData['location_type'] = location_type
            city = get_city_state( newData['latitude'],newData['longitude'])
            newData['city'] = city
            newData['distance_stop'] = resturant['distance']
            locationdata = LocationsSerializer(data=newData)
            if locationdata.is_valid():
                instance = locationdata.save()
                instance.save()
                instance.pit_stop.add(pitstopis)
                # print('new location has been added')
                # return 1
                # print('saving new location')
            else:
                print('serilizer is wrong')
                # return 0
        else:
            # print('already exixts')
            pre_location = Locations.objects.filter(
                longitude=newData['longitude'], latitude=newData['latitude']).first()
            pre_location.pit_stop.add(pitstopis)
            # print('location has been added to t?he existing pitstop')
            # return 1
    return 1
