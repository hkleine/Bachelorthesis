from django.conf.urls import url
from . import views
from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path

# URL-Router der bestimmt unter welcher URL ein View erreichbar ist.
urlpatterns = [
    url(r'^main$', views.mainView, name='mainView'),
    url(r'^$', views.mainView, name='mainView'),
    url(r'^admin/', admin.site.urls),
    url(r'^sensor$', views.post_data, name='post_data'),
    url(r'^token$', views.request_token, name='request_token'),
    url(r'^login$', views.loginView, name='loginView'),
    url(r'^logout$', views.logoutView, name='logout'),
    url(r'^register$', views.registerView, name='register'),
    # Die Macadresse wird über die URL übergeben, damit der Sever weiß welcher Raum gelöscht werden soll
    path('deleteRoom/<macAddress>', views.deleteRoomView, name='deleteRoom'),
    url(r'^addroom$', views.addroomView, name='addroomView'),
]
