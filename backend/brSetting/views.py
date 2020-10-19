from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from brSetting.serializer import ConfigurationSerializer
from brSetting.models import Configuration

def __get_configuration():
    if Configuration.objects.exists() == False:
        #Empty table, return error
        return Response({'detail': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)

    firstConfiguration = Configuration.objects.first()
    serializer = ConfigurationSerializer(firstConfiguration)
    return Response(serializer.data)

def __create_configuration(request):
    if Configuration.objects.exists():
        #Non empty table, return error
        return Response({'detail': 'Not allowed to create more than 1 configuration'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ConfigurationSerializer(data=request.data)
    if serializer.is_valid() == False:
        return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data)

def __update_configuration(request):
    if Configuration.objects.exists() == False:
        #Empty table, return error
        return Response({'detail': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)

    firstConfiguration = Configuration.objects.all()[0]
    serializer = ConfigurationSerializer(firstConfiguration, data=request.data)
    if serializer.is_valid() == False:
        return Response({'detail': 'Data validation failed'}, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data)



@api_view(['GET', 'POST', 'PUT'])
def get_configuration(request):
    if request.method == 'GET':
        return __get_configuration()
    elif request.method == 'POST':
        return __create_configuration(request)
    elif request.method == 'PUT':
        return __update_configuration(request)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
