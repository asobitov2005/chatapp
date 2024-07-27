from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Room, Message

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'user_list.html', {'users': users})


@login_required
def HomeView(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('user_list')  # Handle user not found scenario

        # Check if the room exists in either configuration
        room = Room.objects.filter(
            (models.Q(user1=request.user) & models.Q(user2=user)) |
            (models.Q(user1=user) & models.Q(user2=request.user))
        ).first()

        if not room:
            # Create a new room if it doesn't exist
            room = Room.objects.create(user1=request.user, user2=user)

        return redirect('room', room_pk=room.pk, username=username)

    return redirect('user_list')


@login_required
def RoomView(request, room_pk, username):
    room = get_object_or_404(Room, pk=room_pk)

    # Ensure the user is part of the room
    if not (room.user1 == request.user or room.user2 == request.user):
        return HttpResponseForbidden("You are not allowed to access this room.")

    messages = Message.objects.filter(room=room)

    return render(request, 'room.html', {
        'room_pk': room_pk,
        'username': username,
        'messages': messages,
    })


@login_required
def CreateRoomView(request, username):
    user = get_object_or_404(User, username=username)

    room = Room.objects.filter(
        (Q(user1=request.user) & Q(user2=user)) |
        (Q(user1=user) & Q(user2=request.user))
    ).first()

    if not room:
        room = Room.objects.create(user1=request.user, user2=user)

    return redirect('room', room_pk=room.pk, username=request.user.username)