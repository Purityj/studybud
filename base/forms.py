from django.forms import ModelForm
from .models import Room

# create a modelform
class RoomForm(ModelForm):
    class Meta:
        model = Room  #model whose data you want to be in the form
        fields = '__all__' #the fields in the model you want to be in the form
