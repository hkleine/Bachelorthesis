from django.shortcuts import render, redirect
from .serializers import DataSerializer, SensorSerializer
from django.http import JsonResponse
from .models import Data, Sensor
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
from .token import Token
from .climate_observation_unit import climate_observation_unit
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from itertools import chain
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt

# Datenchnitstelle an welche die Sensordaten geschickt werden.
# Die Schnittstelle kann über den link 127.0.0.1/sensor erreicht werden.
# Sie erwartet ein JSON Objekt das die Macadresse, die Humidity und die Temperature enthält.
@csrf_exempt
def post_data(request):
    # Die Schnittstelle soll nur auf HTTP Post Anfragen reagieren.
    if request.method == "POST":
        # Request enthält den Body des HTTP Post und wird vom JSON Parser geparst.
        data = JSONParser().parse(request)
        # Macadresse und den Token vom Sensor hier zwischen speichern.
        mac = data.get('macAddress')
        token = data.get('token')
        # Query DB nach Macadresse.
        try:
            sensor = Sensor.objects.get(macAddress=mac)
        except Sensor.DoesNotExist:
            sensor = None
        # Prüft ob Macadresse und Sensor zusammen passen.
        # Prüft außerdem ob ob der Sensor vorhanden ist, ob die gesendete Macadresse mit der in der Datenbank übereinstimmt
        # und prüft ob der Token und stimmt.
        if sensor is not None and sensor.token == token and sensor.token is not '':
            # Mit den geprasten Daten wird dann ein Serializer Objekt erstellt.
            serializer = DataSerializer(data=data)
            # Das Serializer Objekt wird dann darauf geprüft ob es der vorgegebenen Form aus der Serializer Klasse entspricht.
            # In diesem Fall wird geprüft ob es sich dabei um Data handelt welche aus Mac, Humidity und Temp bestehen.
            if serializer.is_valid():
                # Ist das Serializer Objekt valide wird es in die Datenbank als Data gespeichert.
                serializer.save()
                # Klimaprüfung der neu eingegangenen Messdaten, daraufhin wird der Status des Sensors geändert.
                cou = climate_observation_unit()
                sensor.state = cou.check_climate(data, sensor)
                sensor.save()
                return HttpResponse("True")
            else:
                return HttpResponse("Not valid")
        else:
            return HttpResponse("Mac and Token do not match")


@csrf_exempt
def request_token(request):
    # Ab hier wartet die Schnittstelle auf ein HTTP Post.
    # Die Post Schnittstelle wird von dem Sensor genutzt um kontinuierlich zu erfragen ob er bereits in der DB vorhanden ist.
    if request.method == "POST":
        # Request enthält den Body des HTTP Post und wird vom JSON Parser geparst.
        data = JSONParser().parse(request)
        # Die Macadresse wird hier zwischen gespeichert um sie dann für eine DB Query zu verwenden.
        mac = data.get('macAddress')
        # DB Query mit Macaddresse.
        if Sensor.objects.filter(macAddress=mac).count() != 0:
            # Macadresse ist in DB vorhanden.
            # Checkt ob der Sensor mit der ermittelten Mac schon einen Token hat.
            if not Sensor.objects.get(macAddress=mac).token:
                # Token wird erstellt.
                authToken = Token.createToken()
                # Token wird in die Tabelle des jeweiligen Sensor gespeichert
                Sensor.objects.filter(macAddress=mac).update(token=authToken)
                Sensor.objects.filter(macAddress=mac).update(state='1')
                return HttpResponse(authToken)
            else:
                return HttpResponse("False")
        else:
            # Macadresse ist nicht in DB vorhanden.
            return HttpResponse("False")


# Die Hauptseite
def mainView(request):
    # Schickt bei einem GET wenn ein User angemeldet ist die main.html an den Browser.
    if request.method == "GET" and request.user.is_authenticated:
        delta = timedelta(days=1)
        last_24_hours = timezone.now() - delta
        # Die DB wird nach allen dem User zugehörigen Sensoren gefragt.
        user_sensors = Sensor.objects.filter(userID=request.user).order_by('date_added')
        # Hier wird eine Liste aller Data's von einem User zusammen geführtself.
        user_data = []
        latest_data_list = []
        for sensor in user_sensors:
            # Filtert nach den Datensätzen die den Sensoren des User entprechen und nicht älter als 24 Std sind.
            sensor_data = Data.objects.filter(macAddress=sensor.macAddress).filter(timestamp__gt=last_24_hours)
            # Diese Daten werden dann zu einer Liste zusammen gefügt.
            user_data = list(chain(user_data, sensor_data))
            try:
                latest_data = sensor_data.latest('timestamp')
                latest_data_list.append(latest_data)
            except:
                latest_data_list.append(0)
                if  sensor.token:
                    # Ändert Status zu "No Data"
                    sensor.state = '1'
                    sensor.save()

        return render(request, 'sensorapp/main.html', {'user_sensors': user_sensors, 'user_data': user_data, 'latest_data_list': latest_data_list})

    elif request.method == "POST" and request.user.is_authenticated:
        pass
    # Ist kein User eingeloggt wird man an die Loginseite weitergeleitet
    else:
        return redirect('/login', {})

# Register-Seite
def registerView(request):
    # Wenn ein ausgefülltes Formular zum Server gesendet wird, wird dieser Teil ausgeführt.
    if request.method == 'POST':
        # Mit den Daten aus dem POST-Request wird ein internes Formular erzeugt.
        f = CustomUserCreationForm(request.POST)
        # Das Formular wird auf seine Validität, mit den Clean-Methoden der Form-Klasse, geprüft.
        if f.is_valid():
            # Wenn das Formular valide ist wird der Benutzer in der DB angelegt.
            user = f.save()
            # Der Client zeigt dem Benutzer optisch, dass die Registrierung erfolgreich war.
            messages.success(request, 'Account created successfully')
            # Der Benutzer wird mit seinen Daten eingeloggt.
            username = request.POST['username']
            password = request.POST['password1']
            request.session.set_expiry(3600)
            login(request, user)
            # Nachdem Login wird der Benutzer zum Dashboard weitergeleitet.
            return redirect('/main', {})
    # Handelt es sich um ein GET wird die Seite nur dem leeren Formular geladen. 
    else:
        f = CustomUserCreationForm()

    return render(request, 'sensorapp/register.html', {'form': f})

# Die Loginseite
def loginView(request):
    # Schickt bei einem GET die login.html an den Browser zusammen mit dem erstellten LoginForm aus der forms.py.
    if request.method == "GET":
        # Erzeugt ein leeres Login-Formular und übergibt dieses zusammen mit der login.html.
        f = LoginForm()
        return render(request, 'sensorapp/login.html', {'form': f})

    # Bekommt die login.html ein POST Request handelt es sich dabei um ein ausgefülltes Login-Formular.
    elif request.method == "POST":
        # Es wird wieder ein Login-Formular erzeugt, dieses mal wird es aber mit dem Formular aus erhaltenen POST Request gefüllt.
        f = LoginForm(request.POST)
        # Username und Passwort werden aus dem Formular extrahiert.
        username = request.POST['username']
        password = request.POST['password']
        # Mit der authenticate Methode von Django wird jetzt der User in der DB gesucht und gegebenfalls Authentifiziert.
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session.set_expiry(86400)
            login(request, user)
            return redirect('/main', {})
        else:
            messages.error(request, 'Wrong username or password')
            return redirect('/login', {})

# Loggt den User aus wenn der Logout-Button gedrückt wird.
def logoutView(request):
    logout(request)
    return redirect('/login', {})

# Die Addroom-Seite kann einen Room für den eingeloggten Benutzer erstellen.
def addroomView(request):
    # Läd bei einem Get die Seite mit dem leeren Formular.
    if request.method == "GET" and request.user.is_authenticated:
        f = RoomForm()
        return render(request, 'sensorapp/addroom.html', {'form': f})

    # Bei einem Post erhält der Server das gefüllte Formular.
    elif request.method == "POST" and request.user.is_authenticated:
        f = RoomForm(request.POST, request=request)
        # Das Formular wird validiert und gegebenfalls wird anschließend ein neuer Sensor in der Datenbank angelegt.
        if f.is_valid():
            obj = f.save(commit=False)
            current_user = request.user
            obj.userID = current_user
            obj.save()
            messages.success(request, 'Room added successfully')
            return redirect('/addroom', {})
    else:
        return redirect('/login', {})

    return render(request, 'sensorapp/addroom.html', {'form': f})

# Wird aufgerufen wenn ein Room gelöscht wird, dabei wird über die URL die Macadresse übergeben.
def deleteRoomView(request, macAddress):
    # DB Query nach der Macaddresse.
    Sensor.objects.get(macAddress=macAddress).delete()
    return redirect('/main', {})
