from django.conf import settings
from django.contrib import admin
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from .views import homeView, contactView

# Because we overrode the need for the e-mail to be filled out when registering
from .forms import EmailFreeRegistrationForm
from registration.backends.simple.views import RegistrationView


urlpatterns = [
    url(r'^$', homeView, name='home'),
    url(r'^typer/', include('typer.urls'), name='typer'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^accounts/', RegistrationView.as_view(form_class=EmailFreeRegistrationForm), name='register'),
    url(r'^contact/', contactView, name='contact'),
]
