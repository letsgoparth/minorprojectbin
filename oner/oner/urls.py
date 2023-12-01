from django.contrib import admin
from django.urls import path
from theapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('add',views.add)
]
