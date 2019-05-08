
from django import forms
from .models import *
from django.forms import ModelForm
import re
from django.core.exceptions import ValidationError

# Login Formular welches den Usernamen und das Passwort entgegen nimmt.
class LoginForm(forms.Form):
    username = forms.CharField(label='Enter Username', min_length=4, max_length=20)
    password = forms.CharField(label='Enter password', widget=forms.PasswordInput, max_length=30)

    labels = {
        "username": "Username", "password": "Password",
    }

# Das Formular mit dem ein Benutzer einen Raum auf seinem Dashboard hinzufügen kann.
class RoomForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RoomForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Sensor
        fields = ['roomName', 'roomType', 'macAddress']
        labels = {
            "macAddress": "Mac Address",
            "roomName": "Room Name",
            "roomType": "Room Type",
        }

    # Die Methode checkt ob es sich bei der eingegebenen Macadresse tatsächlich um eine Macadresse handelt
    # und ob diese nicht schon vergeben ist.
    def clean_macAddress(self):
        macAddress = self.cleaned_data['macAddress']
        all_sensor = Sensor.objects.all()

        r = all_sensor.filter(macAddress=macAddress)

        #Checkt ob es sich bei der Form um eine valide Mac-Adresse handelt
        valid_mac = re.match(r"[a-fA-F0-9]{2}[:][a-fA-F0-9]{2}[:][a-fA-F0-9]{2}[:][a-fA-F0-9]{2}[:][a-fA-F0-9]{2}[:][a-fA-F0-9]{2}", macAddress)
        if not valid_mac:
            raise ValidationError('Not a valid MAC Address')

        #Checkt ob die Mac-Adresse bereits existiert
        if r.count():
            raise ValidationError("MAC Address already exists")
        return macAddress


    # Checkt ob der Raumname bereits von dem Benutzer verwendet wird.
    def clean_roomName(self):
        roomName = self.cleaned_data['roomName']
        user_rooms = Sensor.objects.filter(userID=self.request.user)
        if user_rooms.filter(roomName=roomName).exists():
            raise ValidationError("Room name already exists")
        return roomName



# Das Formular zum Registrieren eines Benutzers.
class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Username', min_length=4, max_length=20)
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name', min_length=2, max_length=150)
    last_name = forms.CharField(label='Last Name', min_length=2, max_length=150)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, max_length=30)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput, max_length=30)
    gender = forms.ChoiceField(label="Select your gender", choices=GENDER_CHOICES, widget=forms.Select(),)
    birthday = forms.DateField(label="Birthday", widget=forms.SelectDateWidget(years=range(date.today().year, 1930, -1)))
    accepted_agbs = forms.BooleanField(label='I read the AGBs')

    # Methoden um die einzelnen Felder des Formular zu überprüfen.
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name'].lower()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name'].lower()
        return last_name

    def clean_gender(self):
        gender = self.cleaned_data['gender']
        return gender

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        return birthday

    def clean_accepted_agbs(self):
        birthday = self.cleaned_data['accepted_agbs']
        return birthday

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password1'],
            gender=self.cleaned_data['gender'],
            birthday=self.cleaned_data['birthday'],
            accepted_agbs=self.cleaned_data['accepted_agbs']
        )
        return user
