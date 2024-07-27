from django.urls import path
from .views import SignUpView, LoginView, UserListView, RoomView, CreateRoomView, MessageListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='auth-signup'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('rooms/<int:room_pk>/', RoomView.as_view(), name='room'),
    path('rooms/create/<str:username>/', CreateRoomView.as_view(), name='create-room'),
    path('rooms/<int:room_pk>/messages/', MessageListView.as_view(), name='message-list'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
