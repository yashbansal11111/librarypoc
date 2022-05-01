"""librarypoc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from librarymanagement import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/',views.uploadcsv, name= 'main'),
    path('activate/<uidb64>/<token>', views.activate, name = 'activate' ),
    path('staffactivate/<uidb64>/<token>', views.staffactivate, name = 'staffactivate' ),
    path('registration/<uidb64>', views.passwordgeneration, name = 'passwordgeneration'),
    path('staffregistration/<uidb64>',
          views.staffpasswordgeneration,
          name = 'staffpasswordgeneration'
          ),
    path('loginpage/', views.loginpage, name = 'loginpage'),
    path('issuebook/', views.issuebook, name = 'issuebook'),
    path('logout/',views.logoutpage,name='logoutpage'),
    path('staffentry/', views.staffentry, name = 'staffentry'),
    path('studententry/', views.studententry, name = 'studententry'),
    path('viewbook/', views.viewbook, name = 'viewbook'),
    path('resetpassword/', views.resetpassword, name = 'resetpassword')

]
