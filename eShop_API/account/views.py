from django.shortcuts import render
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.utils.timezone import timedelta
from django.core.mail import send_mail

from django.utils.crypto import get_random_string   # to get random string

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password      # to convert into hash code in database
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from .serializers import SignUpSerializer, UserSerializer

from utils.helpers import get_current_host

@api_view(['POST'])
def register(request):
    data = request.data

    user = SignUpSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(username = data['email']).exists():
            user = User.objects.create(
                first_name = data['first_name'],
                last_name = data['last_name'],
                email = data['email'],
                username = data['email'],
                password = make_password(data['password'])
            )
            return Response({
                'message':'User registered'
            }, status.HTTP_201_CREATED)
        else:
            return Response({
                'message':'User already exists.'
            }, status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user)
    print(user)
    return Response(user.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):

    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.username = data['email']
    user.email = data['email']

    if data['password'] != "":
        user.password = make_password(data['password'])

    user.save()

    serializer = UserSerializer(user, many=False)

    return Response({
        'user':serializer.data
    }, status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def forgot_password(request):
    data = request.data

    user = get_object_or_404(User, email=data['email'])
    
    token = get_random_string(40)
    expire_date = datetime.now() + timedelta(minutes=30)    # adding 30min to now time to expire.

    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date

    user.profile.save()

    host = get_current_host(request)    # from above function. importing form utils.helpers

    #       "http://localhost:8000/api/reset_password/{token}"
    link = "{host}api/reset_password/{token}".format(host=host, token=token)
    body = "Your reset password link is : {link}".format(link=link)

    send_mail(
        "password reset for eShop",
        body,
        "noreply@eShop.com",
        [data['email']],
    )

    return Response({
        'details':"Password reset email sent to: {email}".format(email=data['email'])
    })

@api_view(['POST'])
def reset_password(request, token):
    data = request.data

    user = get_object_or_404(User, profile__reset_password_token=token) # profile-reset password token should match the token we are giving as input

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error':'token is expired.'}, status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error':'passwords are not same.'}, status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_oassword_expire = None

    user.profile.save()
    user.save()

    return Response({'details':'password reset successfully.'})

