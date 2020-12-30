# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import WatchList, BGTask, PortFolio, ScanEntry
from .serializers.watchlist import WatchListSerializer
from .serializers.bgtask import BGTaskSerializer
from .serializers.portfolio import PortFolioSerializer
from .serializers.scan import ScanEntrySerializer
from .actions.bgtask import start_bgtask

logger = logging.getLogger('django')


@api_view(['GET', 'POST'])
def watchlist_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        #Get the list of watchlists
        watchlist = WatchList.objects.all()
        serializer = WatchListSerializer(watchlist, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def watchlist_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        watchlist = WatchList.objects.get(pk=pk)
    except WatchList.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = WatchListSerializer(watchlist)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WatchListSerializer(watchlist, data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        watchlist.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def bgtask_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        #Get the list of watchlists
        bgtask = BGTask.objects.all()
        serializer = BGTaskSerializer(bgtask, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        serializer = BGTaskSerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        start_bgtask(bgtask)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def bgtask_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        bgtask = BGTask.objects.get(pk=pk)
    except BGTask.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = BGTaskSerializer(bgtask)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BGTaskSerializer(bgtask, data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        start_bgtask(bgtask)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        bgtask.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def portfolio_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        #Get the list of watchlists
        portfolio_list = PortFolio.objects.all()
        serializer = PortFolioSerializer(portfolio_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        serializer = PortFolioSerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def portfolio_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        portfolio = PortFolio.objects.get(pk=pk)
    except PortFolio.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = PortFolioSerializer(portfolio)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PortFolioSerializer(portfolio, data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        portfolio.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def scan_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        #Get the list of watchlists
        scan_list = ScanEntry.objects.all()
        serializer = ScanEntrySerializer(scan_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        serializer = ScanEntrySerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def scan_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        scan = ScanEntry.objects.get(pk=pk)
    except ScanEntry.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = ScanEntrySerializer(scan)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ScanEntrySerializer(scan, data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        scan.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
