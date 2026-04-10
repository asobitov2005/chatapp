from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, ListCreateAPIView, get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from chat.models import Room, Message, get_or_create_private_room
from .serializers import RoomSerializer, MessageSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SignUpView(APIView):
    @swagger_auto_schema(
        operation_description="Register a new user and return JWT tokens.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description='User created and JWT tokens returned',
                examples={
                    'application/json': {
                        'refresh': 'string',
                        'access': 'string',
                    }
                }
            ),
            400: openapi.Response(
                description='Validation errors',
                examples={
                    'application/json': {
                        'username': ['This field is required.'],
                        'password': ['This field is required.']
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Authenticate user and return JWT tokens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response(
                description='JWT tokens',
                examples={
                    'application/json': {
                        'refresh': 'string',
                        'access': 'string',
                    }
                }
            ),
            401: openapi.Response(
                description='Invalid credentials',
                examples={
                    'application/json': {
                        'error': 'Invalid credentials'
                    }
                }
            )
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


class RoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_pk):
        room = get_object_or_404(Room, pk=room_pk)
        if room.user1 != request.user and room.user2 != request.user:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RoomSerializer(room)
        return Response(serializer.data)


class CreateRoomView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create or get a chat room with a specified user",
        responses={
            201: RoomSerializer,
            404: 'User not found'
        },
        manual_parameters=[
            openapi.Parameter(
                'username',
                openapi.IN_PATH,
                description="Username of the user to create a room with",
                type=openapi.TYPE_STRING
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Username of the user to create a room with')
            }
        ),
    )
    def post(self, request, username):
        user = get_object_or_404(User, username=username)

        if user == request.user:
            return Response({"detail": "You cannot create a room with yourself."}, status=status.HTTP_400_BAD_REQUEST)

        room = get_or_create_private_room(request.user, user)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageListView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room = self.get_room()
        return Message.objects.filter(room=room).select_related('sender')

    def get_room(self):
        room = get_object_or_404(Room, pk=self.kwargs.get('room_pk'))
        if room.user1 != self.request.user and room.user2 != self.request.user:
            raise PermissionDenied("You are not allowed to access this room.")
        return room

    def post(self, request, room_pk):
        room = self.get_room()

        message = (request.data.get('message') or '').strip()
        if not message:
            return Response({'message': ['This field may not be blank.']}, status=status.HTTP_400_BAD_REQUEST)

        message_obj = Message.objects.create(room=room, sender=request.user, message=message)
        serializer = MessageSerializer(message_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
