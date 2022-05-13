import csv
import io
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from librarymanagement.models import LibraryRegistration, Student, BookData, IssueBook, Staff
from librarymanagement.forms import IssueBookForm, PasswordForm, LoginForm, EntryForm, StaffPasswordForm, StudentEntryForm, PasswordResetForm, ExistingUserPassResetForm, StudentEditForm, BookDataForm
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
                    updated.save()
                    domain = get_current_site(request).domain
                    uid = urlsafe_base64_encode(force_bytes(updated.pk))
                    token = account_activation_token.make_token(updated)
                    email_subject = 'University Library - Activate your Student Account'
                    email_body = render_to_string('librarymanagement/student/email_activation.html', {
                        'updated': updated,
                        'domain': domain,
                        'uid':urlsafe_base64_encode(force_bytes(updated.pk)),
                        'token':account_activation_token.make_token(updated),
                    })
                    recipient = (updated.email,)
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
            return render(request,'librarymanagement/response/upload_successfull.html')


def activate(request, uidb64, token):
    """This is a function for validating student for activating student's email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Student.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active or user.open_link is True:
            return HttpResponse('Link is expired, to request for a new link\
                                 go to the loginpage, hit reset password\
                                 and enter your details,\
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
    """This is a function for validating staff for activating staff's email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Staff.objects.get(pk=uid)
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
    user = Staff.objects.get(pk=uid)
    user_email = user.email
    user_first_name = user.first_name
    user_last_name = user.last_name
    user_phone = user.phone
    user_activation_link = user.activation_link
    if request.method == 'GET':
        password_gen_form = StaffPasswordForm(instance = user_email)
        context = {'form':password_gen_form}
        return render(request, 'librarymanagement/password_generation.html', context)
    else:
        password_gen_form = StaffPasswordForm(instance = user_email)
        pwd = request.POST['password1']
        pwd2 = request.POST['password2']
        special_sym =['$', '@', '#', '%', '!', '*']
        if len(pwd)>=8 and any((char.isupper(), char.islower(), char.isdigit()) for char in pwd) and any(char in special_sym for char in pwd) :
            if pwd == pwd2:
                staff = LibraryRegistration.objects.create_user(username = user_email,
                                                                password = pwd,
                                                                first_name = user_first_name,
                                                                last_name = user_last_name,
                                                                phone = user_phone,
                                                                activation_link = user_activation_link,
                                                                is_staff = True
                                                                )
                user.open_link = False
                user.is_active = True
                user.save()
                staff.save()
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


def loginpage(request):
    """This is a login function for logging users into their library account"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/loginpage.html', {'loginform':LoginForm()} )
    else:
        login_form = LoginForm(request.POST)
        obj = LibraryRegistration.objects.get(username = request.POST['username'])
        user = authenticate(request,
                               username = request.POST['username'],
                               password = request.POST['password1']
                               )
        if obj.is_active is False:
            context = {'loginform':login_form,'error':"The user seems to be inactive!"}
            return render(request, 'librarymanagement/loginpage.html', context)
        if user is None:
            context = {'loginform':login_form,'error':"Username or password didnt match"}
            return render(request, 'librarymanagement/loginpage.html', context)
        else:
            login(request, user)
            if obj.is_staff is False:
                return redirect('studentportal')
            else:
                return redirect('staffportal')


@login_required
def studentportal(request):
    """This is a function with which students can issue books from library"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/student/studentportal.html')


@login_required
def issuebook(request):
    """This is a function with which students will be able to send book issue request to the staff"""
    if request.method == 'GET':
        context = {'issuebookform':IssueBookForm()}
        return render(request, 'librarymanagement/student/issue_book.html', context)
    else:
        book_obj = BookData.objects.get(pk = request.POST['select_book'])
        issue_form = IssueBookForm(request.POST)
        obj = issue_form.save(commit=False)
        obj.username = request.user
        print(obj.select_book,'++++')
        print(obj.is_pending,'******')
        print(obj.is_subscription_active,'-----')
        if obj.is_pending is False:
            if book_obj.quantity>0:
                obj.username = request.user
                obj.is_pending = True
                obj.request_date = datetime.now()
                obj.save()
                return render(request, 'librarymanagement/response/book_request_sent.html')
            else:
                return render(request, 'librarymanagement/student/issue_book.html', {'error':'Book Out of Stock.'})
        else:
            return render(request, 'librarymanagement/student/issue_book.html', {'error':'You already have an active subscription for the selected Book, please select another!'})


@login_required
def subscriptions(request):
    """This is a function with which students can check their active subscriptions"""
    if request.method == "GET":
        user_obj = IssueBook.objects.filter(username = request.user)
        return render(request, 'librarymanagement/student/subscriptions.html',{'user_obj':user_obj})


@login_required
def bookreturn(request, student_pk):
    """This is a function with which students can perform book return actions"""
    if request.method == "POST":
        student_obj = get_object_or_404(IssueBook, pk = student_pk)
        student_obj.is_returned = True
        student_obj.is_subscription_active = False
        student_obj.is_approved = True
        student_obj.actual_return_date = datetime.now()
        book_obj = BookData.objects.get(bookname = student_obj.select_book)
        book_obj.quantity = book_obj.quantity + 1
        book_obj.save()
        student_obj.save()
        return redirect(subscriptions)


@login_required
def trackrequests(request):
    """With this function students can track their book issue requests"""
    if request.method == "GET":
        user_obj = IssueBook.objects.filter(username = request.user)
        return render(request, 'librarymanagement/student/trackrequests.html',{'user_obj':user_obj})
    

@login_required
def browsebook(request):
    """With this function students can browse and search for books that are available in the library"""
    if request.method == 'GET':
        book_list = BookData.objects.all()
        return render(request, 'librarymanagement/student/browse_book.html', {'book_list':book_list})
    else:
        search_query = request.POST.get('search_box')
        book_list = list(BookData.objects.values_list('bookname',flat=True))
        if search_query not in book_list:
            context = {'error':'Sorry, Book is yet to be available in our Library!'}
            return render(request, 'librarymanagement/student/browse_book.html', context)
        else:
            book_list = BookData.objects.all()
            bookname = BookData.objects.get(bookname = search_query)
            return render(request,'librarymanagement/student/browse_book.html',{'bookname':bookname, 'book_list':book_list})


@login_required
def subhistory(request):
    """This is a function with which students can check their previous subscriptions"""
    if request.method == "GET":
        user_obj = IssueBook.objects.filter(username = request.user)
        return render(request, 'librarymanagement/student/subhistory.html',{'user_obj':user_obj})


@login_required
def staffportal(request):
    """This is a function for displaying homepage of the staff portal"""
    if request.method == 'GET':
        return render(request, 'librarymanagement/staff/staffportal.html')


@login_required
def studentlist(request):
    """This is a function with which staff can get student details with the help of search fields provided in the function"""
    if request.method == "GET":
        return render(request,'librarymanagement/staff/student_list.html')
    else:
        search_query = request.POST.get('search_box')
        student_list = list(Student.objects.values_list('email',flat=True))
        if search_query not in student_list:
            context = {'error':'User does not exist!'}
            return render(request, 'librarymanagement/staff/student_list.html', context)
        else:
            student = Student.objects.get(email = search_query)
            student_row = Student.objects.filter(email = search_query)
            return render(request,'librarymanagement/staff/student_list.html',{'student_row':student_row,'student_list':student})


@login_required
def activestudents(request):
    """With this function staff can view complete list of active students"""
    active_students = Student.objects.filter(is_active = True)
    return render(request, 'librarymanagement/staff/active_students.html',{'active_students':active_students})

@login_required
def inactivestudents(request):
    """With this function staff can view complete list of inactive students"""
    inactive_students = Student.objects.filter(is_active = False)
    return render(request, 'librarymanagement/staff/inactive_students.html',{'inactive_students':inactive_students})
    

@login_required
def editstudent(request, student_pk):
    """With this function staff can edit a student's details and that will be saved to student's database"""
    student_obj = get_object_or_404(Student, pk = student_pk)
    if request.method == "GET":
        student_edit_form = StudentEditForm(instance=student_obj)
        return render(request, 'librarymanagement/staff/edit_student.html', {'student_obj':student_obj,'student_edit_form':student_edit_form})
    else:
        student_edit_form = StudentEditForm(request.POST, instance=student_obj)
        user_obj = LibraryRegistration.objects.get(username = student_obj.email)
        if student_edit_form.is_valid():
            user_obj.first_name = request.POST['first_name']
            user_obj.last_name = request.POST['last_name']
            user_obj.phone = request.POST['phone']
            student_edit_form.save()
            user_obj.is_active = student_obj.is_active
            user_obj.save()
            return render(request,'librarymanagement/response/changes_saved.html')


@login_required
def checkrequests(request):
    """This is a function for showing requests sent by students to staff"""
    if request.method == "GET":
        user_obj = IssueBook.objects.filter(is_pending = True)
        return render(request, 'librarymanagement/staff/checkrequests.html',{'user_obj':user_obj})


@login_required
def allapprovedrequests(request):
    """This is a function for showing all the approved requests by staff"""
    if request.method == "GET":
        user_obj = IssueBook.objects.filter(is_approved = True)
        return render(request, 'librarymanagement/staff/approved_requests.html',{'user_obj':user_obj})


@login_required
def allrejectedrequests(request):
    """This is a function for showing all the rejected requests by staff"""
    if request.method == "GET":
        user_obj = IssueBook.objects.filter(is_rejected = True)
        return render(request, 'librarymanagement/staff/rejected_requests.html',{'user_obj':user_obj})


@login_required
def approverequests(request, student_pk):
    """With this function staff can approve student's book issue requests"""
    if request.method == "POST":
        student_obj = get_object_or_404(IssueBook, pk = student_pk)
        student_obj.is_pending = False
        student_obj.is_approved = True
        student_obj.is_subscription_active = True
        student_obj.review_date = datetime.now()
        input_days = request.POST.get('specify_days')
        if input_days == "":
            student_obj.select_no_of_days = 7
            student_obj.expected_return_date = datetime.now() + timedelta(days=student_obj.select_no_of_days)
        else:
            student_obj.select_no_of_days = int(input_days)
            student_obj.expected_return_date = datetime.now() + timedelta(days=student_obj.select_no_of_days)
        book_obj = BookData.objects.get(bookname = student_obj.select_book)
        if book_obj.quantity>0:
            book_obj.quantity = book_obj.quantity - 1
            book_obj.save()
            student_obj.save()
            return redirect(checkrequests)
        else:
            return render(request, 'librarymanagement/checkrequests.html', {'error':'You cannot approve book request which is Out of Stock.'})


@login_required
def rejectrequests(request, student_pk):
    """With this function staff can reject student's book issue requests"""
    if request.method == "POST":
        student_obj = get_object_or_404(IssueBook, pk = student_pk)
        student_obj.is_pending = False
        student_obj.is_rejected = True
        student_obj.review_date = datetime.now()
        student_obj.save()
        return redirect(checkrequests)


@login_required
def checkbookstock(request):
    """This function shows stock/quantity of books available in the library"""
    if request.method == "GET":
        return render(request, 'librarymanagement/staff/checkbookstock.html')
    else:
        search_query = request.POST.get('search_box')
        book_list = list(BookData.objects.values_list('bookname',flat=True))
        if search_query not in book_list:
            context = {'error':'Sorry, Book not found!'}
            return render(request, 'librarymanagement/staff/checkbookstock.html', context)
        else:
            book_stock = BookData.objects.get(bookname = search_query)
            return render(request,'librarymanagement/staff/checkbookstock.html',{'book_stock':book_stock})


@login_required
def booksliststaff(request):
    """This function shows complete list of books available in the library"""
    if request.method == "GET":
        booksliststaff = BookData.objects.all()
        return render(request, 'librarymanagement/staff/booksliststaff.html',{'booksliststaff':booksliststaff})

@login_required
def addbooks(request):
    allbookdata = BookData.objects.all()
    booklist = list(BookData.objects.values_list('bookname', flat=True))
    
    if request.method == "GET":
        book_form = BookDataForm()
        return render(request, 'librarymanagement/staff/add_books.html', {'book_form':book_form, 'allbookdata':allbookdata})
    else:
        book_form = BookDataForm(request.POST)
        book_name = request.POST['bookname']
        quantity = request.POST['quantity']
        if book_form.is_valid():
            if request.POST['quantity']<='0':
                context = context = {'book_form':book_form, 'allbookdata':allbookdata, 'error':"Book quantity cannot be 0 or negative!"}
                return render(request, 'librarymanagement/staff/add_books.html', context)
            else:
                if book_name in booklist:
                    currentbook = BookData.objects.get(bookname = book_name)
                    currentbook.quantity = currentbook.quantity + int(quantity)
                    currentbook.save()
                    return redirect('booksliststaff')
                else:
                    book = BookData.objects.create(bookname = book_name,
                                                    quantity = quantity,
                                                    )
                    return redirect('booksliststaff')

@login_required
def deletebooks(request, book_pk):
    book_obj = get_object_or_404(BookData, pk = book_pk)
    if request.method=='POST':
        book_obj.delete()
        return redirect('booksliststaff')


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
                user = Staff.objects.create(email = request.POST['username'],
                                            first_name = request.POST['first_name'],
                                            last_name = request.POST['last_name'],
                                            phone = request.POST['phone'],
                                            is_staff = True
                                            )
                return render(request, 'librarymanagement/response/database_update.html')
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
                return render(request, 'librarymanagement/response/database_update.html')
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


def resetpassword(request):
    """This is a function for sending activating link again to users who failed to create their passwords"""
    if request.method == 'GET':
        password_reset_form = PasswordResetForm()
        context = {'password_reset_form':password_reset_form}
        return render(request, 'librarymanagement/reset_password.html', context)
    else:
        password_reset_form = PasswordResetForm(request.POST)
        email = request.POST['username']
        user_list = list(LibraryRegistration.objects.values_list('username', flat=True))
        student_list = list(Student.objects.values_list('email',flat=True))
        staff_list = list(Staff.objects.values_list('email',flat=True))
        if email in student_list:
            student_obj = Student.objects.get(email = email)
            if email not in user_list and student_obj.open_link is True and student_obj.is_active is False:
                domain = get_current_site(request).domain
                uid = urlsafe_base64_encode(force_bytes(student_obj.pk))
                token = account_activation_token.make_token(student_obj)
                email_subject = 'University Library - Create your password and activate your Student Account'
                email_body = render_to_string('librarymanagement/student/email_activation.html', {
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
                return render(request, 'librarymanagement/response/act_link_sent.html')
            elif email in user_list:
                user_obj = LibraryRegistration.objects.get(username = email)
                if user_obj.is_active is True:
                    domain = get_current_site(request).domain
                    uid = urlsafe_base64_encode(force_bytes(user_obj.pk))
                    token = account_activation_token.make_token(user_obj)
                    email_subject = 'University Library - Reset your Password for your Student Account'
                    email_body = render_to_string('librarymanagement/student/email_reset_password.html', {
                        'updated': user_obj,
                        'domain': domain,
                        'uid':urlsafe_base64_encode(force_bytes(user_obj.pk)),
                        'token':account_activation_token.make_token(user_obj),
                    })
                    send_email = EmailMessage(
                            email_subject,
                            email_body,
                            'noreply@librarian.com',
                            (email,)
                    )
                    send_email.send(fail_silently=False)
                    return render(request, 'librarymanagement/response/reset_link_sent.html')
            else:
                context = {'password_reset_form':password_reset_form,'error':'Email does not exist!'}
                return render(request, 'librarymanagement/reset_password.html', context)
        elif email in staff_list:
            staff_obj = Staff.objects.get(email = email)
            if email not in user_list and staff_obj.is_staff and staff_obj.open_link is True and staff_obj.is_active is False:
                domain = get_current_site(request).domain
                uid = urlsafe_base64_encode(force_bytes(staff_obj.pk))
                token = account_activation_token.make_token(staff_obj)
                email_subject = 'University Library - Create your password and activate your Staff Account'
                email_body = render_to_string('librarymanagement/staff/staff_email_activation.html', {
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
                return render(request, 'librarymanagement/response/act_link_sent.html')
            elif email in user_list:
                user_obj = LibraryRegistration.objects.get(username = email)
                if user_obj.is_active and user_obj.is_staff is True:
                    domain = get_current_site(request).domain
                    uid = urlsafe_base64_encode(force_bytes(user_obj.pk))
                    token = account_activation_token.make_token(user_obj)
                    email_subject = 'University Library - Reset your Password for your Staff Account'
                    email_body = render_to_string('librarymanagement/staff/staff_email_reset_password.html', {
                        'updated': user_obj,
                        'domain': domain,
                        'uid':urlsafe_base64_encode(force_bytes(user_obj.pk)),
                        'token':account_activation_token.make_token(user_obj),
                    })
                    send_email = EmailMessage(
                            email_subject,
                            email_body,
                            'noreply@librarian.com',
                            (email,)
                    )
                    send_email.send(fail_silently=False)
                    return render(request, 'librarymanagement/response/reset_link_sent.html')
            else:
                context = {'password_reset_form':password_reset_form,'error':'Email does not exist!'}
                return render(request, 'librarymanagement/reset_password.html', context)
        else:
            context = {'password_reset_form':password_reset_form,'error':'Email does not exist!'}
            return render(request, 'librarymanagement/reset_password.html', context)

def studentpassreset(request, uidb64, token):
    """This is a function for validating student for resetting existing student password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = LibraryRegistration.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active is True:
            return redirect(existinguserpassreset, user_pk = user.pk)
    else:
        return HttpResponse('Link is invalid or expired!\
                             It seems your account is not active, please activate your account by contacting the staff')

def staffpassreset(request, uidb64, token):
    """This is a function for validating staff for resetting existing staff password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = LibraryRegistration.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.is_active and user.is_staff is True:
            return redirect(existinguserpassreset, user_pk = user.pk)
    else:
        return HttpResponse('Link is invalid or expired!\
                             It seems your account is not active, please activate your account by contacting the staff')

def existinguserpassreset(request, user_pk):
    """This is a function for changing existing user password"""
    if request.method == 'GET':
        context = {'exisiting_pass_reset_form':ExistingUserPassResetForm()}
        return render(request, 'librarymanagement/existing_password_reset.html', context)
    else:
        exisiting_pass_reset_form = ExistingUserPassResetForm(request.POST)
        user_obj = LibraryRegistration.objects.get(pk = user_pk)
        new_password = request.POST['password2']
        confirm_password = request.POST['password3']
        if exisiting_pass_reset_form.is_valid():
            if new_password == confirm_password:
                user_obj.set_password(new_password)
                user_obj.save()
                return render(request,'librarymanagement/response/pass_update_success.html')
            else:
                context = {'exisiting_pass_reset_form':ExistingUserPassResetForm(),"error":"New and Confirm new password don't match!"}
                return render(request,'librarymanagement/existing_password_reset.html',context)
        else:
            context = {'exisiting_pass_reset_form':ExistingUserPassResetForm(),'error':'Please check the fields again!'}
            return render(request,'librarymanagement/existing_password_reset.html', context)

# def existinguserpassreset(request, user_pk):
#     """This is a function for changing existing user password"""
#     if request.method == 'GET':
#         context = {'exisiting_pass_reset_form':ExistingUserPassResetForm()}
#         return render(request, 'librarymanagement/existing_password_reset.html', context)
#     else:
#         exisiting_pass_reset_form = ExistingUserPassResetForm(request.POST)
#         user_obj = LibraryRegistration.objects.get(pk = user_pk)
#         old_password = request.POST['password1']
#         new_password = request.POST['password2']
#         confirm_password = request.POST['password3']
#         if exisiting_pass_reset_form.is_valid():
#             if user_obj.check_password(old_password):
#                 if old_password == new_password:
#                     if new_password == confirm_password:
#                         user_obj.set_password(new_password)
#                         user_obj.save()
#                         return render(request,'librarymanagement/response/pass_update_success.html')
#                     else:
#                         context = {'exisiting_pass_reset_form':ExistingUserPassResetForm(),"error":"New and Confirm new password don't match!"}
#                         return render(request,'librarymanagement/existing_password_reset.html',context)
#                 else:
#                     context = {'exisiting_pass_reset_form':ExistingUserPassResetForm(),"error":"Old password and New password cannot be same!"}
#                     return render(request,'librarymanagement/existing_password_reset.html',context)
#             else:
#                 context = {'exisiting_pass_reset_form':ExistingUserPassResetForm(),"error":"Old password doesn't match with Database!"}
#                 return render(request,'librarymanagement/existing_password_reset.html',context)
#         else:
#             context = {'exisiting_pass_reset_form':ExistingUserPassResetForm(),'error':'Please check the fields again!'}
#             return render(request,'librarymanagement/existing_password_reset.html', context)


def logoutpage(request):
    """This is a logout function"""
    if request.method=='POST':
        logout(request)
        return redirect('loginpage')
    else:
        return HttpResponse('Failed.')
