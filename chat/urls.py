from django.urls import path
from .views import signup, login_view, user_list, HomeView, RoomView, CreateRoomView, logout_view

urlpatterns = [
    path('accounts/signup/', signup, name='signup'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),

    path('user_list/', user_list, name='user_list'),
    path('room/<int:room_pk>/<str:username>/', RoomView, name='room'),
    path('create_room/<str:username>/', CreateRoomView, name='create_room'),


    path('', HomeView, name='home'),
]
