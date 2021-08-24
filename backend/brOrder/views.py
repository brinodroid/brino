from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

import logging
from .models import OpenOrder, ExecutedOrder, CancelledOrder
import brOrder.order_bll as order_bll
import brCore.watchlist_bll as watchlist_bll
from brCore.models import WatchList, ScanEntry
from common.actions.scanner import Scanner
from .serializer import OpenOrderSerializer, ExecutedOrderSerializer, CancelledOrderSerializer

logger = logging.getLogger('django')

@transaction.atomic
@api_view(['POST'])
# Input request contains:
# request.data.order: Mandatory
# request.data.strategy: Optional
def create_order_strategy(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'POST':
        # Create a new orders
        serializer = OpenOrderSerializer(data=request.data['order'])
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        # The order is valid
        try:
            # Take the lock
            Scanner.getInstance().get_lock().acquire()

            # Check if the watch list contains the watchlist_id_list
            if 'watchlist_id_list' in serializer.validated_data.keys():
                watchlist_id = serializer.validated_data['watchlist_id_list']
                try:
                    watchlist = WatchList.objects.get(pk=int(watchlist_id))
                except WatchList.DoesNotExist:
                    logger.error('create_order_strategy: WatchList not found {}'.format(
                        serializer.Meta.model))
                    return Response({'detail': 'Watchlist id unknown'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Provided watchlist info in the json. Create the watchlist
                watchlist = watchlist_bll.create_watchlist_if_not_exists_from_json(request.data['watchlist'])

            submitted_order = order_bll.submit_limit_order(serializer, request.data['strategy'], watchlist)

            serializer = OpenOrderSerializer(submitted_order)
            return Response(serializer.data)

        finally:
            # Release the lock
            Scanner.getInstance().get_lock().release()


    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def open_order_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of orders
        order = OpenOrder.objects.all()
        serializer = OpenOrderSerializer(order, many=True)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@transaction.atomic
@api_view(['GET', 'PUT', 'DELETE'])
def open_order_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        order = OpenOrder.objects.get(pk=pk)
    except OpenOrder.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = OpenOrderSerializer(order)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OpenOrderSerializer(order, data=request.data)
        if serializer.is_valid() == order:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        order_bll.delete_order(order)
        serializer = OpenOrderSerializer(order)
        #Send back the content which has been deleted
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def executed_order_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of orders
        order = ExecutedOrder.objects.all()
        serializer = ExecutedOrderSerializer(order, many=True)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def executed_order_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        order = ExecutedOrder.objects.get(pk=pk)
    except OpenOrder.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = ExecutedOrderSerializer(order)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def cancelled_order_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of orders
        order = CancelledOrder.objects.all()
        serializer = CancelledOrderSerializer(order, many=True)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def cancelled_order_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        order = CancelledOrder.objects.get(pk=pk)
    except OpenOrder.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = CancelledOrderSerializer(order)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
