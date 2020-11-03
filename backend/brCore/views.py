# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import WatchList, BGTask, PortFolio
from .serializers.watchlist import WatchListSerializer
from .serializers.bgtask import BGTaskSerializer
from .serializers.portfolio import PortFolioSerializer
from .bgtask_lib import start_bgtask


@api_view(['GET', 'POST'])
def watchlist_list(request):
    if request.method == 'GET':
        #Get the list of watchlists
        watchlist = WatchList.objects.all()
        serializer = WatchListSerializer(watchlist, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        print("request data: %s", request.data)
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid() == False:
            print(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def watchlist_detail(request, pk):
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
            print(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        watchlist.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def bgtask_list(request):
    if request.method == 'GET':
        #Get the list of watchlists
        bgtask = BGTask.objects.all()
        serializer = BGTaskSerializer(bgtask, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        print("request data: %s", request.data)
        serializer = BGTaskSerializer(data=request.data)
        if serializer.is_valid() == False:
            print(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def bgtask_detail(request, pk):
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
            print(serializer.errors)
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
    print("list request data: %s", request.data)
    if request.method == 'GET':
        #Get the list of watchlists
        portfolio_list = PortFolio.objects.all()
        serializer = PortFolioSerializer(portfolio_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        #Create a new watchlist
        print("request data: %s", request.data)
        serializer = PortFolioSerializer(data=request.data)
        if serializer.is_valid() == False:
            print(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def portfolio_detail(request, pk):
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
            print(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        portfolio.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
