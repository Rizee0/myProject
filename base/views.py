from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .form import RoomForm, UserForm, MyUserCreationForm


# Create your views here.


def loginPage(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.warning(request, 'User does not exist!')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'Username or Password is incorrect!')
            

    context = {
            'page': page
    }
    return render(request, 'base/login_register.html', context)

def register(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect('login')
        else:
            messages.error(request, 'An error occurred in usercreations!')
    context = {
        'form': form
    }

    return render(request, 'base/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q)|
                                Q(name__icontains=q)|
                                Q(host__username__icontains=q)
    ).order_by('-created')
    topic = Topic.objects.all()
    room_count = Room.objects.all().count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
    context = {
        'rooms': rooms,
        "topics": topic,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)

def room(request, pk):
    rooms = Room.objects.get(id=pk)
    room_messages = rooms.message_set.all().order_by("-created")
    participants = rooms.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = rooms,
            body = request.POST.get('body')
        )
        rooms.participants.add(request.user)
        return redirect('room', pk=rooms.id)
    context = {
        'rooms': rooms, 'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def profilePage(request, pk):

    q = request.GET.get('q') if request.GET.get("q") != None else ''
    
    user = User.objects.get(id=pk)
    user_rooms = user.room_set.all()
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q)|
                                Q(host__username__icontains=q))
    room_count = Room.objects.all().count()
    room_messages = user.message_set.all().order_by('-created')
    topics = Topic.objects.all()

    context = {
        'topics': topics,"room_messages": room_messages,
        'user': user,
        'rooms': rooms,
        'room_count': room_count,
        'user_rooms': user_rooms,
        'room-messages': room_messages,

    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateProfile(request, pk):
    user = User.objects.get(id=pk)
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')


    context = {
        'form': form,

    }
    return render(request, 'base/update_user.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context = {
        'form': form
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    page = 'update'
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed!')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')     

    context = {
        'room': room, 'form': form, 'page':page,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {
        'obj': room
    }
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.method == "POST":
        message.delete()
        return redirect('home')

    context = {
        'obj': message
    }

    return render(request, 'base/delete.html', context)

def topicsBrowse(request):
    topics = Topic.objects.all()
    rooms = Room.objects.all()
    context = {
        'topics': topics, 'rooms': rooms,
    }
    return render(request, 'base/topics.html', context)

def activity(request):
    room_messages = Message.objects.all()

    context = {
        'room_messages': room_messages

    }
    return render(request, 'base/activity.html', context)

def deleteP(request, pk):
    room = Room.objects.get(id=pk)
    obj = request.user
    if request.method == 'POST':
        room.participants.remove(request.user)
        return redirect('room', pk=room.id)

    context = {
        'obj': obj,
    }
    return render(request, 'base/delete.html', context)