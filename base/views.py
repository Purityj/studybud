from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm

# rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend Developers'},
# ]

# don't name your view login since a django method called login already exists
def loginPage(request):
     #we need this page var to use in the template so that when the page==login, only login is displayed else register page is displayed
    page = 'login' 

    # if user is logged in, they should not be able to login again
    if request.user.is_authenticated:
        return redirect('home')
    
    # get login details
    if request.method =='POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        # check if user exists using try except and flash message
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist') #flash message

        #if user exists, then authenticate (check that creds are correct) else the method will give an error
        user = authenticate(request, username=username, password=password)
        
        # if user exists, then login the user. login() django method will 
        # add the session in the db and login the user then return to homepage
        if user is not None:
            login(request, user)
            return redirect('home')
        # if user is not logged in then display this flash message
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    # logout() method will delete the session token, there4 deleting the user
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    # process the form
    if request.method == 'POST':
        # request.POST is all the cred: password, username that we send
        form = UserCreationForm(request.POST)
        # check if the form have valid creds
        if form.is_valid():
            # save the form but first freeze it(commit=False) 
            # so that we can access the user that has just been created and 
            # check their data and do some cleaning of that data
            user = form.save(commit=False)
            # one of the cleaning - convert username to lowercase
            user.username = user.username.lower()
            user.save()
            # log the user in after saving their creds
            login(request, user)
            # sedn user to homepage
            return redirect('home')
        else:
            # in case error occured when registering
            messages.error(request, 'An error occured during registration. Try again!')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
     #q is whatever is passed to the url like the topic name
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # list all rooms. topic__name --> means quering upwards to the parent
    # use Q to enable the use o(f &, |. To be able to filter by topic name, or room creator name or room description 
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__contains=q)    |
        Q(description__icontains=q)
        )
    # list all topics 
    topics = Topic.objects.all()

    # no. of rooms available
    room_count = rooms.count()

    # recent activities
    room_messages = Message.objects.all()

    context = {'rooms': rooms, 'topics': topics, 
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()  #give us all the messages that are related to this room
    participants = room.participants.all()

    # processing the room_message form
    if request.method == 'POST':
        # create() would create the actual message
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')  #body is from roon.html template
        )
        #this would work without this line, but we're putting it to ensure that the page reloads correctly and that we're back on the ooom page
        return redirect('room', pk=room.id)  
    context = {'room': room, 'room_messages': room_messages, 
               'participants': participants}
    room.participants.add(request.user) #add user as participant automatically after posting
    return render(request, 'base/room.html', context)

# a view for the form
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST) #pass all the form POST data to a var called form
        if form.is_valid():     #checks if form data is valid 
            form.save()       #save the model data in the db
            return redirect('home') # redirect user to homepage. N/B url path to home is called home in url.py

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# update room view
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)  #get the object you want to update and we are getting the value by id, whic is the primary key(pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!')

    # processing update room form
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) #replace old form(instance=room) with the new form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

# delete room view
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

# delete message
# work on delete message and edit message. For some reason delete message has pk errors
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed to delete this message!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html',  {'obj':message})