from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from .views import homeView, contactView, profileView

# Because we overrode the need for the e-mail to be filled out when registering
from .forms import EmailFreeRegistrationForm
from django_registration.backends.one_step.views import RegistrationView


urlpatterns = [
    path('', homeView, name='home'),
    path('typer/', include('typer.urls'), name='typer'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('accounts/register', RegistrationView.as_view(form_class=EmailFreeRegistrationForm), name='register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('contact/', contactView, name='contact'),
    path('profile/', profileView, name='profile'),
]
