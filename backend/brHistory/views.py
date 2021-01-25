from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import CallOptionData, PutOptionData
from .serializer import CallOptionDataSerializer, PutOptionDataSerializer

logger = logging.getLogger('django')


# Create your views here.
@api_view(['GET'])
def callhistory_list(request, watchlist_id):
    logger.debug("request data: {}, pk: {}".format(request.data, watchlist_id))
    if request.method == 'GET':
        # Get the list of watchlists
        calloption_history = CallOptionData.objects.filter(watchlist_id=watchlist_id)
        serializer = CallOptionDataSerializer(calloption_history, many=True)
        return Response(serializer.data)
    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def puthistory_list(request, watchlist_id):
    logger.debug("request data: {}, pk: {}".format(request.data, watchlist_id))
    if request.method == 'GET':
        # Get the list of watchlists
        putoption_history = PutOptionData.objects.filter(watchlist_id=watchlist_id)
        serializer = PutOptionDataSerializer(putoption_history, many=True)
        return Response(serializer.data)
    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
