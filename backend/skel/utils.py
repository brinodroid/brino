from brAuth.serializer import UserDataSerializer


def jwt_resp_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserDataSerializer(user, context={'request': request}).data
    }