from django.shortcuts import render

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import UserDataSerializer


@api_view(['GET'])
def user_data_from_token(request):
    """
    Get user data from their token
    """
    serializer = UserDataSerializer(request.user)
    return Response(serializer.data)
