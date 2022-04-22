import csv
import io
from datetime import datetime, timedelta
from MySQLdb import IntegrityError
from django.core.mail import EmailMessage
from django.forms import ValidationError
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from librarymanagement.models import LibraryRegistration, Student, BookData
from librarymanagement.forms import IssueBookForm, PasswordForm, LoginForm, StaffForm, StaffPasswordForm
from .tokens import account_activation_token

# Create your views here.
@permission_required('admin.can_add_log_entry')
def uploadcsv(request):
    """This is a function for uploading CSV file containing student's data"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/uploadcsv.html' )
    else:
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            context = {'error':'This is not a csv file, Please try again.'}
            return render(request, 'librarymanagement/uploadcsv.html', context)
        else:
            try:
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                next(io_string)
                for column in csv.reader(io_string, delimiter='|', skipinitialspace=True):
                    updated, created = Student.objects.update_or_create(
                        first_name = column[0],
                        last_name = column[1],
                        date_of_birth = column[2],
                        email = column[3],
                        phone = column[4]
                    )
                    print(updated,'++++++++++++')
                    print(type(updated),'************')
                    updated.save()
                    domain = get_current_site(request).domain
                    email_subject = 'University Library - Activate your Account'
                    email_body = render_to_string('librarymanagement/email_activation.html', {
                        'updated': updated,
                        'domain': domain,
                        'uid':urlsafe_base64_encode(force_bytes(updated.pk)),
                        'token':account_activation_token.make_token(updated),
                    })
                    # email_recipient = Student.objects.values('email')
                    # email_recipient_lst=[]
                    # for i in email_recipient:
                    #     email_recipient_lst.append(i['email'])
                    recipient = (updated.email,)
                    print(recipient,'-----------')
                    send_email = EmailMessage(
                            email_subject,
                            email_body,
                            'noreply@librarian.com',
                            recipient,
                    )
                    send_email.send(fail_silently=False)
                    
            except(IntegrityError, ValueError, ValidationError):
                return HttpResponse('Please check your CSV file for any missing fields\
                                     and try again.')
            # except Exception as e:
            #     print(e)
            return HttpResponse('Upload Successfull,\
                                Emails are sent to the students\
                                whose emails are yet to be activated.')


# def emailpage(request):
#     if request.method == "GET":
#         context = {'form': LibraryRegisterForm()}
#         return render(request, 'librarymanagement/RegisterPage.html', context)
#     else:
#         # username = request.POST['username']
#         # email = request.POST['email']
#         # password = request.POST['password']

#         # if not User.objects.filter(username=username).exists():
#         #     if not User.objects.filter(email=email).exists():
#         #         if len(password)<6:
#         #             messages.error(request, 'Password Too Short')
#         #             return render(request, 'librarymanagement/RegisterPage.html')

#         #         user = User.objects.create_user(username=username, email=email)
#         #         user.set_password(password)
#         #         user.is_active = False
#         #         user.save()
#         #         messages.success(request, 'Account Successfully Created')
#         #         return render(request, 'librarymanagement/RegisterPage.html')

#         # username = request.POST['username']
#         # email = request.POST['email']
#         # password = request.POST.get('password')

#         # user = Student.objects.create_user(username=username, email=email)
#         # user.set_password(password)
#         # user.is_active = False

#         # user.save()
#         # messages.success(request, 'Account successfully created')

#         form = LibraryRegisterForm(request.POST)
#         if form.is_valid():
#             subject = 'University Library - Generate your password'
#             message = 'Please click the link below to generate your password -'
#             from_email = 'librarian@gmail.com'
#             to_email = request.POST.get('email','') #take email field or provide a blank default
#             #print(type(to_email),'++++++++')
#             #print(request.POST)
#             #print(to_email,'*******')
#             if subject and message and from_email and to_email:
#                 try:
#                     send_mail(subject, message, from_email, [to_email])
#                 except BadHeaderError:
#                     return HttpResponse('Invalid header found.')
#             return HttpResponse('An email has been sent to you. Please click the link in your email to generate you password.')        
#         else:
#             return HttpResponse('Make sure all fields are entered and valid.')


def activate(request, uidb64, token):
    """This is a function for activating student's email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Student.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active is True:
            return HttpResponse('Your email is already activated.\
                                 Please login to your library account to proceed further.')
        else:
            user.is_invited = False
            user.is_active = True
            user.save()
            return redirect(passwordgeneration, uidb64 = uidb64)
    else:
        return HttpResponse('Activation link is invalid or expired!\
                             Either you have already clicked on the link & activated your Email\
                             or the link is expired.')

def passwordgeneration(request, uidb64):
    """This is a function for generating password for creating student's library account"""
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = Student.objects.get(pk=uid).email
    if request.method == 'GET':
        password_gen_form = PasswordForm(instance = user)
        context = {'form':password_gen_form}
        return render(request, 'librarymanagement/password_generation.html', context)
    else:
        password_gen_form = PasswordForm(instance = user)
        if request.POST['password1'] == request.POST['password2']:
            student = LibraryRegistration.objects.create_user(username = user,
                                                              password = request.POST['password1']
                                                              )
            student.save()
            return redirect('loginpage')
        else:
            context = {'form':password_gen_form,'error':"Passwords didn't match"}
            return render(request, 'librarymanagement/password_generation.html', context )

def staffactivate(request, uidb64, token):
    """This is a function for activating student's email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = LibraryRegistration.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active is True:
            return HttpResponse('Your email is already activated.\
                                 Please login to your library portal to proceed further.')
        else:
            user.is_invited = False
            user.is_active = True
            user.save()
            #return HttpResponse('Account Activated please generate your password!!')
            return redirect(staffpasswordgeneration, uidb64 = uidb64)
    else:
        return HttpResponse('Activation link is invalid or expired!\
                             Either you have already clicked on the link & activated your Email\
                             or the link is expired.')

def staffpasswordgeneration(request, uidb64):
    """This is a function for generating password for creating student's library account"""
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = LibraryRegistration.objects.get(pk=uid).username
    if request.method == 'GET':
        password_gen_form = StaffPasswordForm(instance = user)
        context = {'form':password_gen_form}
        return render(request, 'librarymanagement/password_generation.html', context)
    else:
        password_gen_form = StaffPasswordForm(instance = user)
        if request.POST['password1'] == request.POST['password2']:
            staff = LibraryRegistration.objects.get(pk=uid)
            staff.set_password(request.POST['password1'])
            staff.save()
            return redirect('loginpage')
        else:
            context = {'form':password_gen_form,'error':"Passwords didn't match"}
            return render(request, 'librarymanagement/password_generation.html', context )



def loginpage(request):
    """This is a login function for logging student into their library account"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/loginpage.html', {'loginform':LoginForm()} )
    else:
        login_form = LoginForm(request.POST)
        student = authenticate(request,
                               username = request.POST['username'],
                               password = request.POST['password1']
                               )
        if student is None:
            context = {'loginform':login_form,'error':"Username or password didn't match"}
            return render(request, 'librarymanagement/loginpage.html', context)
        else:
            login(request, student)
            return redirect('issuebook')


@login_required
def issuebook(request):
    """This is a function with which students can issue books from library"""
    if request.method == 'GET':
        context = {'issuebookform':IssueBookForm()}
        return render(request, 'librarymanagement/issuebook.html', context)
    else:
        issue_form = IssueBookForm(request.POST)
        obj = issue_form.save(commit=False)
        print(request.user,'-----------')
        obj.username = request.user
        obj.issue_date = datetime.now()
        if obj.select_no_of_weeks == '1':
            obj.return_date = datetime.now() + timedelta(days=7)
        if obj.select_no_of_weeks == '2':
            obj.return_date = datetime.now() + timedelta(days=14)
        if obj.select_no_of_weeks == '3':
            obj.return_date = datetime.now() + timedelta(days=21)
        if obj.select_no_of_weeks == '4':
            obj.return_date = datetime.now() + timedelta(days=28)

        book_obj = BookData.objects.get(pk = request.POST['select_book'])
        print(book_obj,'************')
        print(type(book_obj),'---------')
        book_obj.quantity = book_obj.quantity - 1
        book_obj.save()
        obj.save()
        return HttpResponse('Book Issued Successfully')

# def staffregistration(request):
#     """This is a function with which staff can register to the library portal"""
#     if request.method == 'GET':
#         staff_form = StaffForm()
#         return render(request, 'librarymanagement/staffregistration.html', {'form': staff_form})
#     else:
#         form = StaffForm(request.POST)
#         if form.is_valid():
#             if request.POST['password1'] == request.POST['password2']:
#                 try:
#                     user = LibraryRegistration.objects.create_user(username = request.POST['username'],
#                                                                    password=request.POST['password1'],
#                                                                    email = request.POST['email'],
#                                                                    is_staff = True
#                                                                    )
#                     user.save()
#                     return redirect('stafflogin')
#                 except IntegrityError:
#                     context =  {'form':form, 'error':"This username is already taken,\
#                                                       please use a different username"}
#                     return render(request, 'librarymanagement/staffregistration.html', context)
#         form.save()

# def stafflogin(request):
#     """This is a function with which staff can login to the library portal"""
#     if request.method == 'GET':
#         return render(request, 'librarymanagement/stafflogin.html', {'forms':AuthenticationForm()})
#     else:
#         user = authenticate(request, username=request.POST['username'],
#                             password=request.POST['password'])
#         if user is None:
#             context =  {'forms':AuthenticationForm(), 'error':'Username & Password did not match,\
#                                                                try again'}
#             return render(request, 'librarymanagement/stafflogin.html', context)
#         else:
#             login(request, user)
#             return HttpResponse('Welcome to library portal.')

@permission_required('admin.can_add_log_entry')
def staffentry(request):
    """This is a function with which admin can input staff details to the database"""
    if request.method == 'GET':
        context = {'staff_form': StaffForm()}
        return render(request, 'librarymanagement/staffactivation.html', context)
    else:
        staff_form = StaffForm(request.POST)
        if staff_form.is_valid():
            try:
                user = LibraryRegistration.objects.create(username = request.POST['username'],
                                                          first_name = request.POST['first_name'],
                                                          last_name = request.POST['last_name'],
                                                          phone_no = request.POST['phone_no'],
                                                          is_initial = True,
                                                          is_active = False,
                                                          is_staff = True
                                                          )
                return HttpResponse('activation email sent succesfully')
            except IntegrityError:
                context =  {'staff_form':StaffForm(), 'error':"This username is already taken,\
                                                               please use a different username"}
                return render(request, 'librarymanagement/staffactivation.html', context)
        else:
            staff_form = StaffForm()
            context = {'staff_form':staff_form, 'error':"form didn't validate"}
            return render(request, 'librarymanagement/staffactivation.html', context)

def logoutpage(request):
    """This is a logout function"""
    if request.method=='POST':
        logout(request)
        return redirect('loginpage')
