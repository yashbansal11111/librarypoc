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
    path('main/staffentry/', views.staffentry, name = 'staffentry'),
    path('main/studententry/', views.studententry, name = 'studententry'),
    path('activate/<uidb64>/<token>', views.activate, name = 'activate' ),
    path('staffactivate/<uidb64>/<token>', views.staffactivate, name = 'staffactivate' ),
    path('registration/<uidb64>', views.passwordgeneration, name = 'passwordgeneration'),
    path('staffregistration/<uidb64>', views.staffpasswordgeneration, name = 'staffpasswordgeneration'),
    path('loginpage/', views.loginpage, name = 'loginpage'),
    path('loginpage/resetpassword/', views.resetpassword, name = 'resetpassword'),
    path('resetpassword/<uidb64>/<token>', views.studentpassreset, name = 'studentpassreset' ),
    path('staffresetpassword/<uidb64>/<token>', views.staffpassreset, name = 'staffpassreset' ),
    path('resetpassword/<int:user_pk>/',views.existinguserpassreset, name = 'existinguserpassreset'),

    path('studentportal/home/', views.studentportal, name = 'studentportal'),
    path('studentportal/issue/', views.issuebook, name = 'issuebook'),
    path('studentportal/trackrequests/', views.trackrequests, name = 'trackrequests'),
    path('studentportal/trackrequests/orderbypending/', views.orderbypendingstudent, name = 'orderbypendingstudent'),
    path('studentportal/trackrequests/orderbyapproved/', views.orderbyapprovedstudent, name = 'orderbyapprovedstudent'),
    path('studentportal/trackrequests/orderbyrejected/', views.orderbyrejectedstudent, name = 'orderbyrejectedstudent'),
    path('studentportal/browsebook/', views.browsebook, name = 'browsebook'),
    path('studentportal/subscriptions/', views.subscriptions, name = 'subscriptions'),
    path('studentportal/subscriptions/bookreturn/<int:student_pk>/', views.bookreturn, name = 'bookreturn'),
    path('studentportal/subscriptions/orderbyreturndate/', views.orderbyreturndatestudent, name = 'orderbyreturndatestudent'),
    path('studentportal/subhistory/', views.subhistory, name = 'subhistory'),
    path('studentportal/subhistory/orderbyactualreturndate/', views.orderbyactualreturndate, name = 'orderbyactualreturndate'),
    path('studentportal/browsebook/harry_potter', views.harrypotter, name = 'harrypotter'),
    
    path('staffportal/home/', views.staffportal, name = 'staffportal'),
    path('staffportal/studentlist/', views.studentlist, name = 'studentlist'),
    path('staffportal/studentlist/editstudent/<int:student_pk>/', views.editstudent, name = 'editstudent'),
    path('staffportal/studentlist/activestudents/', views.activestudents, name = 'activestudents'),
    path('staffportal/studentlist/inactivestudents/', views.inactivestudents, name = 'inactivestudents'),
    path('staffportal/studentlist/activestudents/orderbyactiveusername/', views.orderbyactiveusername, name = 'orderbyactiveusername'),
    path('staffportal/studentlist/inactivestudents/orderbyinactiveusername/', views.orderbyinactiveusername, name = 'orderbyinactiveusername'),
    path('staffportal/checkrequests/', views.checkrequests, name = 'checkrequests'),
    path('staffportal/checkrequests/allapprovedrequests', views.allapprovedrequests, name = 'allapprovedrequests'),
    path('staffportal/checkrequests/allapprovedrequests/orderbyreturndate/', views.orderbyreturndate, name = 'orderbyreturndate'),
    path('staffportal/checkrequests/allapprovedrequests/orderbyissuedate/', views.orderbyissuedate, name = 'orderbyissuedate'),
    path('staffportal/checkrequests/allapprovedrequests/orderbynoofdays/', views.orderbynoofdays, name = 'orderbynoofdays'),
    path('staffportal/checkrequests/allrejectedrequests', views.allrejectedrequests, name = 'allrejectedrequests'),
    path('staffportal/checkrequests/allrejectedrequests/orderbyrejectdate/', views.orderbyrejectdate, name = 'orderbyrejectdate'),
    path('staffportal/checkrequests/approve/<int:student_pk>/', views.approverequests, name = 'approverequests'),
    path('staffportal/checkrequests/reject/<int:student_pk>/', views.rejectrequests, name = 'rejectrequests'),
    path('staffportal/checkrequests/orderbyrequestdate/', views.orderbyrequestdate, name = 'orderbyrequestdate'),
    path('staffportal/checkbookstock/', views.checkbookstock, name = 'checkbookstock'),
    path('staffportal/checkbookstock/bookslist/', views.booksliststaff, name = 'booksliststaff'),
    path('staffportal/checkbookstock/bookslist/addbooks/', views.addbooks, name = 'addbooks'),
    path('staffportal/checkbookstock/bookslist/deletebooks/<int:book_pk>/', views.deletebooks, name = 'deletebooks'),
    
    path('logout/',views.logoutpage,name='logoutpage'),
    
    

]
