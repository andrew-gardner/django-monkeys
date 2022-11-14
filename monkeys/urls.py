from django.conf import settings
from django.contrib import admin
from django.urls import include, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from .views import homeView, contactView, profileView

# Because we overrode the need for the e-mail to be filled out when registering
from .forms import EmailFreeRegistrationForm
from django_registration.views import RegistrationView


urlpatterns = [
    re_path(r'^$', homeView, name='home'),
    re_path(r'^typer/', include('typer.urls'), name='typer'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^login/$', auth_views.LoginView.as_view(), {'template_name': 'login.html'}, name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(), {'template_name': 'logged_out.html'}, name='logout'),
    re_path(r'^accounts/', RegistrationView.as_view(form_class=EmailFreeRegistrationForm), name='register'),
    re_path(r'^contact/', contactView, name='contact'),
    re_path(r'^profile/', profileView, name='profile'),
]
