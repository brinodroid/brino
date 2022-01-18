import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

import brGaze.gaze_bll as gaze_bll

logger = logging.getLogger('django')



@api_view(['POST'])
def update_closest_monthly_options(request, watchlist_id):
    logger.info("request data: {}, watchlist_id: {}".format(request.data, watchlist_id))
    if request.method == 'POST':
        gaze_bll.create_closest_options(watchlist_id)

        update_done_msg = 'update_closest_monthly_options: done {}'.format(timezone.now())
        logger.info(update_done_msg)
        return Response({'detail': update_done_msg}, status=status.HTTP_200_OK)


    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def update_closest_monthly_options_for_all_stocks(request):
    if request.method == 'POST':
        gaze_bll.create_closest_options_for_all_stocks()

        update_done_msg = 'update_closest_monthly_options_for_all_stocks: done {}'.format(timezone.now())
        logger.info(update_done_msg)
        return Response({'detail': update_done_msg}, status=status.HTTP_200_OK)


    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def train_lstm(request, watchlist_id):
    if request.method == 'POST':
        gaze_bll.train_lstm(watchlist_id)

        update_done_msg = 'train_lstm: done {}'.format(timezone.now())
        logger.info(update_done_msg)
        return Response({'detail': update_done_msg}, status=status.HTTP_200_OK)


    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def infer_lstm(request, watchlist_id):
    if request.method == 'GET':
        infered_values = gaze_bll.infer_lstm(watchlist_id)

        update_done_msg = 'infer_lstm: done {}'.format(timezone.now())
        logger.info(infered_values)
        return Response({infered_values}, status=status.HTTP_200_OK)


    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)