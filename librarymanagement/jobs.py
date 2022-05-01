from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from librarymanagement.models import LibraryRegistration, Student
from .tokens import account_activation_token
from django.conf import settings

def checkinitialstaff():
    """This function checks for staff having status as initial and sends them mail/
       containing activation link to create a password and activate their account"""
    obj = list(LibraryRegistration.objects.filter(is_initial = True))
    print(obj)

    for i in obj:
        user = LibraryRegistration.objects.get(username = i)
        obj_pk = user.pk

        #domain = get_current_site(request).domain
        #domain = 'localhost:8000'
        domain = settings.HOST_ADDR
        uid = urlsafe_base64_encode(force_bytes(obj_pk))
        token = account_activation_token.make_token(user)
        email_subject = 'University Library - Activate your Staff Account'
        email_body = render_to_string('librarymanagement/staff_email_activation.html', {
                        'updated': user,
                        'domain': domain,
                        'uid':uid,
                        'token':token,
                    })
        recipient = (i,)
        print(recipient,'++++++++')
        send_email = EmailMessage(
                                email_subject,
                                email_body,
                                'noreply@librarian.com',
                                recipient,
                                )
        send_email.send(fail_silently=False)
        user.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
        user.is_initial = False
        user.is_invited = True
        user.save()


def checkinitialstudent():
    """This function checks for staff having status as initial and sends them mail/
       containing activation link to create a password and activate their account"""
    obj = list(Student.objects.filter(is_initial = True))
    print(obj)

    for i in obj:
        user = Student.objects.get(email = i)
        print(user,'+++++++++++++')
        obj_pk = user.pk

        #domain = get_current_site(request).domain
        #domain = 'localhost:8000'
        domain = settings.HOST_ADDR
        uid = urlsafe_base64_encode(force_bytes(obj_pk))
        token = account_activation_token.make_token(user)
        email_subject = 'University Library - Activate your Student Account'
        email_body = render_to_string('librarymanagement/email_activation.html', {
                        'updated': user,
                        'domain': domain,
                        'uid':uid,
                        'token':token,
                    })
        recipient = (i,)
        print(recipient,'++++++++')
        send_email = EmailMessage(
                                email_subject,
                                email_body,
                                'noreply@librarian.com',
                                recipient,
                                )
        send_email.send(fail_silently=False)
        user.activation_link = "http://{}/activate/{}/{}".format(domain, uid, token)
        user.is_initial = False
        user.is_invited = True
        user.save()