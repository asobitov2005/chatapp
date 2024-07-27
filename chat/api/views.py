from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from chat.models import Room, Message
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


class UserListView(ListCreateAPIView):
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

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        room = Room.objects.filter(
            (Q(user1=request.user) & Q(user2=user)) |
            (Q(user1=user) & Q(user2=request.user))
        ).first()

        if not room:
            room = Room.objects.create(user1=request.user, user2=user)

        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageListView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs.get('room_pk')
        return Message.objects.filter(room_id=room_id)

    def post(self, request, room_pk):
        data = request.data
        data['room'] = room_pk
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
