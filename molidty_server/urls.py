
from django.contrib import admin
from django.urls import path
from django.urls import include
from mainapp import urls as mainapp_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(mainapp_urls)),  # Include the mainapp URLs under the 'api/' prefix
]
