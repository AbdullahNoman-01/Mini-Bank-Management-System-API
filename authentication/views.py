from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .import serializers


class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = []

class LoginView(APIView):
   serializer_class = serializers.RegisterSerializer
   permission_classes = []

   def post(self, request):
      username = request.data.get('username')
      password = request.data.get('password')

      user = authenticate(
         request,
         username=username,
         password=password
      )

      if user is not None:
         token, created = Token.objects.get_or_create(user=user)

         return Response({
            'message': 'Login successful',
            'token': token.key
         })

      return Response(
         {'error': 'Invalid username or password'},
         status=status.HTTP_401_UNAUTHORIZED
      )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user