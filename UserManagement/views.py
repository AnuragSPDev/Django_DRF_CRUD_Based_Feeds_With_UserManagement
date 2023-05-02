import random
from datetime import timedelta

from django.contrib.auth import logout, authenticate
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import permissions, authentication
from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT, 
                                   HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, 
                                   HTTP_400_BAD_REQUEST)

from .models import MyUser
from .serializer import RegistrationSerilizer, ForgotPasswordSerializer


# Create your views here.
class RegisterUser(APIView):
    '''
    Class based view for Signing Up the user using APIVIew as base class
    An OTP will be sent to the User to validate email
    '''
    permission_classes = [permissions.AllowAny]
    try:
        def post(self, request):
            data = request.data
            serializer = RegistrationSerilizer(data=data)
            if serializer.is_valid():
                account = serializer.save()
                account.is_active = True

                # send an OTP on the entered email address
                otp = random.randint(100000, 999999)
                print('otp generated: {}'.format(otp))
                account.otp = otp
                account.save()
                send_otp_mail(request)
                return Response({
                    'status': 'User Registered Successfully',
                    'message': {
                        'email': account.email,
                        'information': 'OTP Has Been Sent To The Entered Email, Please Check And Enter OTP To Verify Email And Login',
                    }
                })
            else:
                return Response({
                    'status': 'User Not Registred',
                    'message': serializer.errors
                })

    except Exception as e:
        print('Exception is: ', e)

class ValidateOTPAndGenerateToken(APIView):
    '''
    Class based view for validating user email using APIVIew as base class
    Authentication token will be generated once the user email is verified
    '''
    permission_classes = [permissions.AllowAny]
    try:
        def post(self, request):
            email = request.data.get('email')
            user = MyUser.objects.get(email=email)
            otp_entered = request.data.get('otp')
            otp_generated = user.otp

            if not otp_entered == otp_generated:
                # If entered OTP and OTP in DB doesn't matches
                MyUser.objects.get(email=user.email).delete()
                return Response({
                    'status': HTTP_204_NO_CONTENT,
                    'message': 'Entered OTP Did Not Match, Please Sign In Again'
                })
            
            user.otp_verified = True
            user.email_verified = True
            user.save()
            token = Token.objects.get_or_create(user=user)[0].key
            return Response({
                    'status': 'User Registered Successfully',
                    'message': {
                        'email': user.email,
                        'username': user.username,
                        'date_of_birth': user.date_of_birth,
                        'token': token,
                    }
                })
    except Exception as e:
        print('Exception is: ', e)

class LoginUser(APIView):
    '''
    Class based view for Login-in the user using APIVIew as base class
    Authentication token will be generated once the user logs in
    '''
    permission_classes = [permissions.AllowAny]
    try:
        def post(self, request):
            data = request.data
            email = data.get('email')
            password = data.get('password')
            if email is None or password is None:
                return Response({
                    'status': HTTP_403_FORBIDDEN,
                    'message': 'Both email and password are required'
                })

            user = authenticate(email=email, password=password)
            if not user:
                return Response({
                    'status': HTTP_403_FORBIDDEN,
                    'message': 'Invalid User Credentials'
                })

            email_verified = is_email_verified(user)
            if not email_verified:
                return Response({
                    'status': HTTP_403_FORBIDDEN,
                    'message': 'User Email Not Verified. Please verify Your Email First By Entering The OTP You Received Over Mail.'
                })

            token = Token.objects.get_or_create(user=user)[0].key
            return Response({
                'status': HTTP_200_OK,
                'token': token
            })

    except Exception as e:
        print('Exception is: ', e)

class LogoutUser(APIView):
    '''
    Class based view for Logging out the user using APIVIew as base class
    Authentication token will be deleted once the user logs out
    '''
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    try:
        def get(self, request):
            # breakpoint()
            user = request.user
            email_verified = is_email_verified(user)
            if not email_verified:
                return Response({
                    'status': HTTP_403_FORBIDDEN,
                    'message': 'User Email Not Verified. Please verify Your Email First By Entering The OTP You Received Over Mail.'
                })
            user.auth_token.delete()
            logout(request)
            return Response({
                'status': HTTP_204_NO_CONTENT,
                'message': 'User Logged Out Successfully'
            })
    except Exception as e:
        print('Exception is: ', e)

class ForgotUserPassword(APIView):
    '''
    Class based view for Forgot password functionality for the user using APIVIew as base class
    '''
    permission_classes = [permissions.IsAuthenticated]

    try:
        def patch(self, request):
            data = request.data
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            if old_password is None or new_password is None:
                return Response({
                    'status': HTTP_400_BAD_REQUEST,
                    'message': 'Both Old Password and New Password are required'
                })
            
            serializer = ForgotPasswordSerializer(data=data)
            if serializer.is_valid():
                if not request.user.check_password(old_password):
                    return Response({
                        'status': HTTP_400_BAD_REQUEST,
                        'message': 'Old Password is not correct'
                    })
                request.user.set_password(new_password)
                serializer.save()
                request.user.save()
                return Response({
                    'status': HTTP_200_OK,
                    'message': 'New password saved successfully'
                })

    except Exception as e:
        print('Exception is: ', e)

class IndexPage(APIView):
    '''
    Class based view for the index page using APIVIew as base class
    User must be logged in/authenticated to view this page
    '''
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        email_verified = is_email_verified(user)
        if not email_verified:
            return Response({
                'status': HTTP_403_FORBIDDEN,
                'message': 'User Email Not Verified. Please verify Your Email First By Entering The OTP You Received Over Mail.'
            })
        token_expired = is_token_expired(request.user.auth_token)
        if token_expired:
            request.user.auth_token.delete()
            return Response({
                'status': HTTP_401_UNAUTHORIZED,
                'message': 'Please Login Again To View This Page'
            })
        
        return Response({
            'message': 'This is an index page'
        })

def token_expires_in(token):
    '''
    Function to calculate the time left in token expiration
    :param token: Authentication token assigned to the user
    :returns: time left in authentication token expiration 
    '''
    time_elapsed = timezone.now() - token.created
    time_left = timedelta(seconds = int(settings.TOKEN_EXPIRES_IN)) - time_elapsed
    return time_left

def check_token_expiration(token):
    '''
    Function to check token expiration time with the current time
    :param token: Authentication token assigned to the user
    :returns: True/False based upon token expiration time with the current time
    '''
    return token_expires_in(token) < timedelta(seconds=0)

def is_token_expired(token):
    '''
    Function to check whether the authentication token is expired or not
    :param token: Authentication token assigned to the user
    :returns: True/False based upon authentication token is expired or not
    '''
    is_expired = check_token_expiration(token)
    return is_expired
    # # Regenerate token functionality
    # if is_expired:
    #     # re-generate token
    #     new_token = regenerate(token)
    #     return new_token
    # return token

def regenerate(token):
    '''
    Function to re-generate token
    :param token: Authentication token assigned to the user
    :return: re-generated token
    '''
    token = Token.objects.get_or_create(user = token.user)
    return token

def send_otp_mail(request):
    '''
    Function to send an email to the user containing an OTP to email verification
    '''
    subject = 'OTP for email verification'
    user = MyUser.objects.get(email=request.data.get('email'))
    message = 'Hi {}, \n\n Below is the otp to verify your email \n\n {}'.format(user.username, user.otp)
    from_email = settings.EMAIL_HOST_USER
    if subject and user and message:
        try:
            email = EmailMessage(subject, message, from_email, [user.email])
            email.send()
        except Exception as e:
            print('Exception is: ', e)

def is_email_verified(user):
    '''
    Function to check whether user email is verified or not
    '''
    return True if user.email_verified else False
    