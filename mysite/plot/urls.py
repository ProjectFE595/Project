from django.conf.urls import url

from . import views
app_name = 'plot'

urlpatterns = [
    url(r'^$', views.graphic, name='graphic'),

]