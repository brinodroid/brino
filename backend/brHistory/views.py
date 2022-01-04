from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from django.utils import timezone
from .models import CallOptionData, PutOptionData, StockData
from .serializer import CallOptionDataSerializer, PutOptionDataSerializer, StockDataSerializer
import brHistory.history_bll as history_bll
import brCore.watchlist_bll as watchlist_bll

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

@api_view(['GET'])
def stockhistory_list(request, watchlist_id):
    logger.debug("request data: {}, pk: {}".format(request.data, watchlist_id))
    if request.method == 'GET':
        # Get the list of watchlists
        stockdata_history = StockData.objects.filter(watchlist_id=watchlist_id)
        serializer = StockDataSerializer(stockdata_history, many=True)
        return Response(serializer.data)
    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def history_update(request, watchlist_id):
    logger.debug("request data: {}, pk: {}".format(request.data, watchlist_id))
    if request.method == 'POST':
        # Get the list of watchlists
        watchlist = watchlist_bll.get_watchlist(int(watchlist_id))
        if not watchlist_bll.is_option(watchlist):
            # Its a stock
            history_bll.create_stock_history(watchlist)
            stockdata_history = StockData.objects.filter(watchlist_id=watchlist_id)
            serializer = StockDataSerializer(stockdata_history, many=True)
            return Response(serializer.data)

        # Else its an option
        # TODO: Add option update code as needed

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def history_update_all(request):
    logger.debug("request data: {}".format(request.data))
    if request.method == 'POST':

        # Scan all history
        history_bll.save_history()

        save_done_msg = 'save_history: done {}'.format(timezone.now())
        logger.info(save_done_msg)
        return Response({'detail': save_done_msg}, status=status.HTTP_200_OK)


    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
