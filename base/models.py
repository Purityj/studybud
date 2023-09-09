from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Topic & Room has 1-to-many rlship - a topic can have multiple rooms while a room can only have 1 topic
    # When the Topic table is deleted, we don't want the Room table to be deleted
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #null=True, meaning field can be empty. blank=True, to allow blank/empty forms
    # related_name is being specified because User has already been used in host.
    participants = models.ManyToManyField(User, related_name='participants', blank=True) #all users  active in a room

    # auto_now takes a timestamp everytime we save the instance/row while auto_now_add takes a timestamp of when we first created the model/instance. 
    # If the instacnce is saved multipe times, created value does not change while updated value changes each time
    updated = models.DateTimeField(auto_now=True)  #take timestamp of row when it's updated
    created = models.DateTimeField(auto_now_add=True) #take timestamp of row hen it's created only

    class Meta:
        ordering = ['-updated', '-created']
 
    def __str__(self):
        return self.name
    

class Message(models.Model):
    # user has 1-to-many relationship with message
    # a user can have many messages but a message can belong only to one user
    user = models.ForeignKey(User, on_delete=models.CASCADE) #user sending the message. 1-to-many relationship with Message
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #database relationship - 1-to-many relationship with Room
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)   #take timestamp everytime the row is updated
    created = models.DateTimeField(auto_now_add=True) #take timestamp only when the record/row is created

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] #return only the 1st 50 characters of user's input in the body field to be viewd in django admin panel
        
