import csv
import io
from datetime import datetime, timedelta
from MySQLdb import IntegrityError
from django.core.mail import EmailMessage
from django.forms import ValidationError
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from librarymanagement.models import LibraryRegistration, Student, BookData
from librarymanagement.forms import IssueBookForm, PasswordForm, LoginForm, EntryForm, StaffPasswordForm, StudentEntryForm, PasswordResetForm
from .tokens import account_activation_token

# Create your views here.
@permission_required('admin.can_add_log_entry')
def uploadcsv(request):
    """This is a function for uploading CSV file containing student's data"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/main.html' )
    else:
        try:
            csv_file = request.FILES['file']
        except KeyError:
            context = {'error':'No files selected to upload, please select a file from your system'}
            return render(request, 'librarymanagement/main.html', context)

        if not csv_file.name.endswith('.csv'):
            context = {'error':'This is not a csv file, Please try again.'}
            return render(request, 'librarymanagement/main.html', context)
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
                    uid = urlsafe_base64_encode(force_bytes(updated.pk))
                    token = account_activation_token.make_token(updated)
                    email_subject = 'University Library - Activate your Student Account'
                    email_body = render_to_string('librarymanagement/email_activation.html', {
                        'updated': updated,
                        'domain': domain,
                        'uid':urlsafe_base64_encode(force_bytes(updated.pk)),
                        'token':account_activation_token.make_token(updated),
                    })
                    recipient = (updated.email,)
                    print(recipient,'-----------')
                    send_email = EmailMessage(
                            email_subject,
                            email_body,
                            'noreply@librarian.com',
                            recipient,
                    )
                    send_email.send(fail_silently=False)
                    updated.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
                    updated.is_initial = False
                    updated.is_invited = True
                    updated.save()

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
#         return render(request, 'librarymanagement/register_page.html', context)
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
        if user.is_active or user.open_link is True:
            return HttpResponse('Link is expired, to request for a new link\
                                 go to the loginpage and hit reset password\
                                 a new activation link will be sent to your email,\
                                 use that link to create a new password.')
        else:
            user.is_invited = False
            user.open_link = True
            user.save()
            return redirect(passwordgeneration, uidb64 = uidb64)
    else:
        return HttpResponse('Activation link is invalid or expired!\
                             Either you have already clicked on the link & activated your Email\
                             or the link is expired.')

def passwordgeneration(request, uidb64):
    """This is a function for creating password for creating student's library account"""
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = Student.objects.get(pk=uid)
    user_email = user.email
    user_first_name = user.first_name
    user_last_name = user.last_name
    user_phone = user.phone
    user_activation_link = user.activation_link
    if request.method == 'GET':
        password_gen_form = PasswordForm(instance = user_email)
        context = {'form':password_gen_form}
        return render(request, 'librarymanagement/password_generation.html', context)
    else:
        password_gen_form = PasswordForm(instance = user_email)
        pwd = request.POST['password1']
        pwd2 = request.POST['password2']
        special_sym =['$', '@', '#', '%', '!', '*']
        if len(pwd)>=8 and any((char.isupper(), char.islower(), char.isdigit()) for char in pwd) and any(char in special_sym for char in pwd) :
            if pwd == pwd2:
                student = LibraryRegistration.objects.create_user(username = user_email,
                                                                  password = pwd,
                                                                  first_name = user_first_name,
                                                                  last_name = user_last_name,
                                                                  phone = user_phone,
                                                                  activation_link = user_activation_link
                                                                 )
                user.open_link = False
                user.is_active = True
                user.save()
                student.save()
                return redirect('loginpage')
            else:
                context = {'form':password_gen_form,'error':"Passwords didnt match"}
                return render(request, 'librarymanagement/password_generation.html', context )
        else:
            context = {'form':password_gen_form,'error':"Password should be of atleast 8 characters\
                                                         and contain atleast 1 uppercase, 1 lowercase,\
                                                         1 numeric and 1 special character."
                                                         }
            return render(request, 'librarymanagement/password_generation.html', context )

def staffactivate(request, uidb64, token):
    """This is a function for activating staff's email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = LibraryRegistration.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active or user.open_link is True:
            return HttpResponse('Link is expired, to request for a new link\
                                 go to the loginpage and hit reset password\
                                 a new activation link will be sent to your email,\
                                 use that link to create a new password.')
        else:
            user.is_invited = False
            user.open_link = True
            user.save()
            return redirect(staffpasswordgeneration, uidb64 = uidb64)
    else:
        return HttpResponse('Activation link is invalid or expired!\
                             Either you have already clicked on the link & activated your Email\
                             or the link is expired.')

def staffpasswordgeneration(request, uidb64):
    """This is a function for generating password for creating staff's library account"""
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = LibraryRegistration.objects.get(pk=uid)
    user_username = user.username
    if request.method == 'GET':
        password_gen_form = StaffPasswordForm(instance = user_username)
        context = {'form':password_gen_form}
        return render(request, 'librarymanagement/password_generation.html', context)
    else:
        password_gen_form = StaffPasswordForm(instance = user_username)
        pwd = request.POST['password1']
        pwd2 = request.POST['password2']
        special_sym =['$', '@', '#', '%', '!', '*']
        if len(pwd)>=8 and any((char.isupper(), char.islower(), char.isdigit()) for char in pwd) and any(char in special_sym for char in pwd) :
            if pwd == pwd2:
                #staff = LibraryRegistration.objects.get(pk=uid)
                user.set_password(pwd)
                user.open_link = False
                user.is_active = True
                user.save()
                return redirect('loginpage')
            else:
                context = {'form':password_gen_form,'error':"Passwords didnt match"}
                return render(request, 'librarymanagement/password_generation.html', context )
        else:
            context = {'form':password_gen_form,'error':"Password should be of atleast 8 characters\
                                                         & contain atleast 1 uppercase, 1 lowercase,\
                                                         1 numeric and 1 special character."
                                                         }
            return render(request, 'librarymanagement/password_generation.html', context )

def loginpage(request):
    """This is a login function for logging users into their library account"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/loginpage.html', {'loginform':LoginForm()} )
    else:
        login_form = LoginForm(request.POST)
        obj = LibraryRegistration.objects.get(username = request.POST['username'])
        student = authenticate(request,
                               username = request.POST['username'],
                               password = request.POST['password1']
                               )
        if obj.is_active is False:
            context = {'loginform':login_form,'error':"The user seems to be inactive!"}
            return render(request, 'librarymanagement/loginpage.html', context)
        if student is None:
            context = {'loginform':login_form,'error':"Username or password didnt match"}
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
        book_obj = BookData.objects.get(pk = request.POST['select_book'])
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
        print(book_obj,'************')
        print(type(book_obj),'---------')
        book_obj.quantity = book_obj.quantity - 1
        book_obj.save()
        obj.save()
        return HttpResponse('Book Issued Successfully')

@permission_required('admin.can_add_log_entry')
def staffentry(request):
    """This is a function with which admin can input staff details to the database"""
    if request.method == 'GET':
        context = {'entry_form': EntryForm()}
        return render(request, 'librarymanagement/detail_entry.html', context)
    else:
        entry_form = EntryForm(request.POST)
        if entry_form.is_valid():
            try:
                user = LibraryRegistration.objects.create(username = request.POST['username'],
                                                          first_name = request.POST['first_name'],
                                                          last_name = request.POST['last_name'],
                                                          phone = request.POST['phone'],
                                                          is_initial = True,
                                                          is_active = False,
                                                          is_staff = True
                                                          )
                return HttpResponse('Details saved to database successfully.')
            except IntegrityError:
                context =  {'entry_form':EntryForm(), 'error':"This username is already taken,\
                                                               please use a different username"}
                return render(request, 'librarymanagement/detail_entry.html', context)
        else:
            entry_form = EntryForm()
            if len(request.POST['phone'])>10:
                context = {'entry_form':entry_form,
                           'error':'Contact No. should not be more than 10 digits'
                           }
                return render(request, 'librarymanagement/detail_entry.html', context)
            else:
                context = {'entry_form':entry_form, 'error':"form didnt validate"}
                return render(request, 'librarymanagement/detail_entry.html', context)

@permission_required('admin.can_add_log_entry')
def studententry(request):
    """This is a function with which admin can input student details to the database"""
    if request.method == 'GET':
        context = {'entry_form': StudentEntryForm()}
        return render(request, 'librarymanagement/detail_entry.html', context)
    else:
        entry_form = StudentEntryForm(request.POST)
        if entry_form.is_valid():
            try:
                user = Student.objects.create(email = request.POST['username'],
                                              first_name = request.POST['first_name'],
                                              last_name = request.POST['last_name'],
                                              phone = request.POST['phone'],
                                              date_of_birth = request.POST['date_of_birth']
                                              )
                return HttpResponse('Details saved to database successfully.')
            except IntegrityError:
                context =  {'entry_form':StudentEntryForm(), 'error':"This username is already taken,\
                                                              please use a different username"}
                return render(request, 'librarymanagement/detail_entry.html', context)
        else:
            entry_form = StudentEntryForm()
            if len(request.POST['phone'])>10:
                context = {'entry_form':entry_form,
                           'error':'Contact No. should not be more than 10 digits'
                           }
                return render(request, 'librarymanagement/detail_entry.html', context)
            else:
                context = {'entry_form':entry_form, 'error':"form didnt validate"}
                return render(request, 'librarymanagement/detail_entry.html', context)

def viewbook(request,):
    books = get_object_or_404(BookData)
    if request.method == 'GET':
        return render(request, 'librarymanagement/viewbook.html', {'book':books})

def resetpassword(request):
    if request.method == 'GET':
        password_reset_form = PasswordResetForm()
        context = {'password_reset_form':password_reset_form}
        return render(request, 'librarymanagement/reset_password.html', context)
    else:
        password_reset_form = PasswordResetForm(request.POST)
        email = request.POST['username']
        user_list = list(LibraryRegistration.objects.values_list('username', flat=True))
        student_list = list(Student.objects.values_list('email',flat=True))
        #student_obj = Student.objects.get(email = email)
        #user_obj = LibraryRegistration.objects.get(username = email)
        print(type(email),'//////////////')
        print(student_list,'*/***********')
        print((user_list),'-----------')
        if email in student_list:
            student_obj = Student.objects.get(email = email)
            if email not in user_list and student_obj.open_link is True and student_obj.is_active is False:
                domain = get_current_site(request).domain
                uid = urlsafe_base64_encode(force_bytes(student_obj.pk))
                token = account_activation_token.make_token(student_obj)
                email_subject = 'University Library - Create your password and activate your Student Account'
                email_body = render_to_string('librarymanagement/email_activation.html', {
                    'updated': student_obj,
                    'domain': domain,
                    'uid':urlsafe_base64_encode(force_bytes(student_obj.pk)),
                    'token':account_activation_token.make_token(student_obj),
                })
                send_email = EmailMessage(
                        email_subject,
                        email_body,
                        'noreply@librarian.com',
                        (email,)
                )
                send_email.send(fail_silently=False)
                student_obj.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
                student_obj.open_link = False
                student_obj.is_invited = True
                student_obj.save()
                return HttpResponse('Email has been sent to you.')
            # elif email in user_list:
            #     if len(user_obj.password)>0 and user_obj.is_staff is False and user_obj.is_active is True:
            #         domain = get_current_site(request).domain
            #         uid = urlsafe_base64_encode(force_bytes(student_obj.pk))
            #         token = account_activation_token.make_token(student_obj)
            #         email_subject = 'University Library - Reset your password'
            #         email_body = render_to_string('librarymanagement/email_activation.html', {
            #             'updated': student_obj,
            #             'domain': domain,
            #             'uid':urlsafe_base64_encode(force_bytes(student_obj.pk)),
            #             'token':account_activation_token.make_token(student_obj),
            #         })
            #         send_email = EmailMessage(
            #                 email_subject,
            #                 email_body,
            #                 'noreply@librarian.com',
            #                 (email,)
            #         )
            #         send_email.send(fail_silently=False)
            #         student_obj.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
            #         user_obj.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
            #         student_obj.open_link = False
            #         user_obj.is_active = False
            #         student_obj.is_active = False
            #         user_obj.is_invited = True
            #         student_obj.is_invited = True
            #         student_obj.save()
            #         user_obj.save()
            #         return HttpResponse('Email has been sent to you.')
            # else:
            #     context = {'password_reset_form':password_reset_form,'error':'Email does not exist!'}
            #     return render(request, 'librarymanagement/reset_password.html', context)
        elif email in user_list:
            staff_obj = LibraryRegistration.objects.get(username = email)
            if staff_obj.is_staff and staff_obj.open_link is True and staff_obj.is_active is False:
                domain = get_current_site(request).domain
                uid = urlsafe_base64_encode(force_bytes(staff_obj.pk))
                token = account_activation_token.make_token(staff_obj)
                email_subject = 'University Library - Create your password and activate your Staff Account'
                email_body = render_to_string('librarymanagement/staff_email_activation.html', {
                    'updated': staff_obj,
                    'domain': domain,
                    'uid':urlsafe_base64_encode(force_bytes(staff_obj.pk)),
                    'token':account_activation_token.make_token(staff_obj),
                })
                send_email = EmailMessage(
                        email_subject,
                        email_body,
                        'noreply@librarian.com',
                        (email,)
                )
                send_email.send(fail_silently=False)
                staff_obj.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
                staff_obj.open_link = False
                staff_obj.is_invited = True
                staff_obj.save()
                return HttpResponse('Email has been sent to you.')
            else:
                context = {'password_reset_form':password_reset_form,'error':'Email does not exist!'}
                return render(request, 'librarymanagement/reset_password.html', context)
        else:
            context = {'password_reset_form':password_reset_form,'error':'Email does not exist!'}
            return render(request, 'librarymanagement/reset_password.html', context)

def logoutpage(request):
    """This is a logout function"""
    if request.method=='POST':
        logout(request)
        return redirect('loginpage')
