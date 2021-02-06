# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import WatchList, BGTask, PortFolio, ScanEntry, PortFolioUpdate
from .serializers.watchlist import WatchListSerializer
from .serializers.bgtask import BGTaskSerializer
from .serializers.portfolio import PortFolioSerializer, PortFolioUpdateSerializer
from .serializers.scan import ScanEntrySerializer
from .actions.bgtask import start_bgtask
from .actions.pf_update import PFUpdater
from .types.status_types import Status
from brCore.actions.scanner import Scanner


logger = logging.getLogger('django')


@api_view(['GET', 'POST'])
def watchlist_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of watchlists
        watchlist = WatchList.objects.all()
        serializer = WatchListSerializer(watchlist, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new watchlist
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
        # Get the list of watchlists
        bgtask = BGTask.objects.all()
        serializer = BGTaskSerializer(bgtask, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new watchlist
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
        # Get the list of watchlists
        portfolio_list = PortFolio.objects.all()
        serializer = PortFolioSerializer(portfolio_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new watchlist
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
        # Get the list of watchlists
        scan_list = ScanEntry.objects.all()
        serializer = ScanEntrySerializer(scan_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new watchlist
        serializer = ScanEntrySerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Scanner.getInstance().get_lock().acquire()
            serializer.save()
        finally:
            Scanner.getInstance().get_lock().release()

        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def __delete_unused_portfolio(scan):
    scan_list = ScanEntry.objects.filter(
        portfolio_id=scan.portfolio_id)

    if len(scan_list) > 0:
        # Cannot delete because its used from other scans
        logger.error("Not deleting portfolio {} as its used from {} scans. Eg using scan: {}".format(
            scan.portfolio_id, len(scan_list), scan_list[0]))
        return None

    # No scan is referencing the portfolio. Delete the port folio
    try:
        portfolio = PortFolio.objects.get(pk=scan.portfolio_id)
        portfolio.delete()
        return portfolio
    except PortFolio.DoesNotExist:
        logger.error(
            "Didnt find {} in portfolio. Skipping delete".format(scan.portfolio_id))

    return None


def __delete_unused_watchlist(scan, portfolio):
    scan_list = ScanEntry.objects.filter(
        watchlist_id=scan.watchlist_id)

    if len(scan_list) > 0:
        # Cannot delete the watchlist because its used from other scans
        logger.error("Not deleting watchlist {} as its used from {} scans. Eg using scan: {}".format(
            scan.watchlist_id, len(scan_list), scan_list[0]))
        return None

    portfolio_list = PortFolio.objects.filter(
        watchlist_id=scan.watchlist_id)

    if len(portfolio_list) > 0:
        # Cannot delete the watchlist because its used from other portfolios
        logger.error("Not deleting watchlist {} as its used from {} portfolios. Eg using portfolio: {}".format(
            scan.watchlist_id, len(portfolio_list), portfolio_list[0]))
        return None

    # The watchlist is not used, delete it.
    try:
        watchlist = WatchList.objects.get(pk=scan.watchlist_id)
        watchlist.delete()
        return watchlist
    except WatchList.DoesNotExist:
        logger.error(
            "Didnt find {} in watchlist. Skipping delete".format(scan.watchlist_id))

    return None


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

        try:
            Scanner.getInstance().get_lock().acquire()
            serializer.save()
        finally:
            Scanner.getInstance().get_lock().release()

        return Response(serializer.data)

    elif request.method == 'DELETE':
        try:
            Scanner.getInstance().get_lock().acquire()

            # 1. Delete the scan
            scan.delete()

            # 2. Need to delete portfolio asociated with the scan
            portfolio = __delete_unused_portfolio(scan)

            # 3. Need to delete the watchlist associated with the scan if scan/portfolio is not using the watchlist
            if portfolio != None:
                __delete_unused_watchlist(scan, portfolio)

        finally:
            Scanner.getInstance().get_lock().release()

        return Response({'detail': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
def portfolioupdate_list(request):
    logger.debug("request data: %s", request.data)
    if request.method == 'GET':
        # Get the list of watchlists
        portfolioupdate_list = PortFolioUpdate.objects.all()
        serializer = PortFolioUpdateSerializer(portfolioupdate_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Create a new watchlist
        serializer = PortFolioUpdateSerializer(data=request.data)
        if serializer.is_valid() == False:
            logger.error(serializer.errors)
            return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Acquire the scanner lock to prevent the scanner thread from overwriting updated values

            try:
                Scanner.getInstance().get_lock().acquire()
                PFUpdater.getInstance().update(serializer.validated_data.get('source'))
            finally:
                Scanner.getInstance().get_lock().release()

            serializer.validated_data['status'] = Status.PASS.value
            serializer.validated_data['details'] = 'Success'

        except Exception as e:
            serializer.validated_data['status'] = Status.FAIL.value
            serializer.validated_data['details'] = repr(e)
            serializer.save()

            logger.error('Exception in portfolio update: {}'.format(repr(e)))
            return Response({'detail': repr(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer.save()
        return Response(serializer.data)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
