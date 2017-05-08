from . import serializers

from django.contrib.auth import authenticate, login
from rest_framework import permissions, authentication, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import urllib as urllib2


class UsersList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserOtherSerializer

    def get_queryset(self):
        return get_user_model().objects.all().order_by("username")

    def get_serializer_context(self):
        return {"request": self.request}


class UserMe_R(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    def get_object(self):
        return get_user_model().objects.get(email=self.request.user.email)


class UserOther_R(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        if "uid" in self.kwargs and self.kwargs["uid"]:
            users = get_user_model().objects.filter(id=self.kwargs["uid"])
        elif "email" in self.kwargs and self.kwargs["email"]:
            users = get_user_model().objects.filter(email=self.kwargs["email"])
        else:
            users = None
        if not users:
            self.other = None
            raise exceptions.NotFound
        self.other = users[0]
        return self.other

    def get_serializer_class(self):
        if self.request.user == self.other:
            return serializers.UserMeSerializer
        else:
            return serializers.UserOtherSerializer


class UpdatePosition(generics.UpdateAPIView):
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserMeSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UpdatePosition, self).dispatch(*args, **kwargs)

    def get_object(self):
        return get_user_model().objects.get(email=self.request.user.email)

    def perform_update(self, serializer, **kwargs):
        try:
            lat1 = float(self.request.data.get("lat", False))
            lon1 = float(self.request.data.get("lon", False))
            if lat1 and lon1:
                point = Point(lon1, lat1)
            else:
                point = None

            if point:
                serializer.save(last_location = point)
            return serializer
        except:
            pass


@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
# @csrf_exempt
def token_login(request):
    if (not request.GET["username"]) or (not request.GET["password"]):
        return Response({"detail": "Missing username and/or password"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.GET["username"], password=request.GET["password"])
    if user:
        if user.is_active:
            login(request, user)
            try:
                my_token = Token.objects.get(user=user)
                return Response({"token": "{}".format(my_token.key)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": "Could not get token"})
        else:
            return Response({"detail": "Inactive account"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Invalid User Id of Password"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def register(request):
    print (request.GET)

    if (not request.GET["username"]) or (not request.GET["password"] or (not request.GET["email"])):
        return Response({"detail": "Missing username and/or password and/or email"}, status=status.HTTP_400_BAD_REQUEST)
        print("no values")
    try:
        user = get_user_model().objects.get(username=request.GET["username"])
        if user:
            print("user already exists")
            return Response({"detail": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
    except get_user_model().DoesNotExist:
        user = get_user_model().objects.create_user(username=request.GET["username"])

        # Set user fields provided
        print(request.GET["password"] + request.GET["firstname"] + request.GET["lastname"] + request.GET["email"])
        user.set_password(request.GET["password"])
        user.first_name = request.GET["firstname"]
        user.last_name = request.GET["lastname"]
        user.email = request.GET["email"]
        user.save()
        print("done")

        return Response({"detail": "Successfully created"}, status=status.HTTP_201_CREATED)

@api_view(["GET", ])
@permission_classes((permissions.AllowAny,))
@csrf_exempt
def get_station_data(request):
    file = urllib2.urlopen(
        'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=f8ea8c86300204fae0f3231a3664c4c2e499bea5')
    data = file.read()
    file.close()
    print(data)
    return Response({"data": data}, status=status.HTTP_200_OK)
    

