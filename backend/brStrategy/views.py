from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
import json

from brStrategy.models import Strategy
from brStrategy.serializer import StrategySerializer
import brStrategy.strategy_bll as strategy_bll


logger = logging.getLogger('django')


@api_view(['GET', 'POST'])
def strategy_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of strategies
        strategy_list = Strategy.objects.all()
        serializer = StrategySerializer(strategy_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new strategy
        strategy = strategy_bll.create_strategy(request.data)
        serializer = StrategySerializer(strategy)
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
def strategy_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        strategy = Strategy.objects.get(pk=pk)
    except Strategy.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = StrategySerializer(strategy)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StrategySerializer(strategy, data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Need to validate if portfolio supports the strategy_type
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        strategy.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_200_OK)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
