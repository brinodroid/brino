from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import Order
from .serializer import OrderSerializer

logger = logging.getLogger('django')


@api_view(['GET', 'POST'])
def order_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of orders
        order = Order.objects.all()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new orders
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
def order_detail(request, pk):
    logger.debug("request data: %s, pk: %s", request.data, str(pk))
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'detail': 'Resource does not exist'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid() == order:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        order.delete()
        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
