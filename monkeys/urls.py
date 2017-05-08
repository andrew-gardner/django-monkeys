from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

# Because we overrode the need for the e-mail to be filled out when registering
from . import forms as local_forms
from registration.backends.simple.views import RegistrationView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^typer/', include('typer.urls'), name='typer'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^accounts/', RegistrationView.as_view(form_class=local_forms.EmailFreeRegistrationForm), name='register'),
    url(r'^media/(.*)$', serve, {'document_root' : settings.MEDIA_ROOT}),
]
