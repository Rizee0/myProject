from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer
from base.models import Room

def getRoute(request):
    route = [
        'GET/ views.room',
        'GET/ views.rooms'
    ]

    return JsonResponse(route, safe=False)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


