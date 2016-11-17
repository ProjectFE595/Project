"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [

    # The url() function is passed four arguments, two required: regex and view,
    # and two optional: kwargs, and name.

    url(r'^interface/', include('interface.urls')),
    url(r'^plot/', include('plot.urls')),
    url(r'^expreturn/', include('expreturn.urls')),

    # When Django finds a regular expression match, Django calls the specified view function, with an HttpRequest
    # object as the first argument and any "captured" values from the regular expression as other arguments.

    url(r'^admin/', admin.site.urls),
    # You should always use include() when you include other URL patterns.
    # admin.site.urls is the only exception to this.
]