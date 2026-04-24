from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Room, Message, get_or_create_private_room


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("user_list")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("user_list")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "user_list.html", {"users": users})


@login_required
def HomeView(request):
    return redirect("user_list")


@login_required
def RoomView(request, room_pk):
    room = get_object_or_404(Room.objects.select_related("user1", "user2"), pk=room_pk)

    if not (room.user1 == request.user or room.user2 == request.user):
        return HttpResponseForbidden("You are not allowed to access this room.")

    messages = Message.objects.filter(room=room).select_related("sender")
    other_user = room.user2 if room.user1 == request.user else room.user1

    return render(
        request,
        "room.html",
        {
            "room_pk": room_pk,
            "current_username": request.user.username,
            "other_username": other_user.username,
            "messages": messages,
        },
    )


@login_required
@require_POST
def CreateRoomView(request, username):
    user = get_object_or_404(User, username=username)

    if user == request.user:
        return redirect("user_list")

    room = get_or_create_private_room(request.user, user)
    return redirect("room", room_pk=room.pk)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")
