from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from librarymanagement.models import Student, Staff
from .tokens import account_activation_token

def checkinitialstaff():
    """This function checks for staff having status as initial and sends them mail/
       containing activation link to create a password and activate their account"""
    obj = list(Staff.objects.filter(is_initial = True))
    for i in obj:
        user = Staff.objects.get(email = i)
        obj_pk = user.pk
        domain = settings.HOST_ADDR
        uid = urlsafe_base64_encode(force_bytes(obj_pk))
        token = account_activation_token.make_token(user)
        email_subject = 'University Library - Activate your Staff Account'
        email_body = render_to_string('librarymanagement/staff/staff_email_activation.html', {
                        'updated': user,
                        'domain': domain,
                        'uid':uid,
                        'token':token,
                    })
        recipient = (i,)
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
    for i in obj:
        user = Student.objects.get(email = i)
        obj_pk = user.pk
        #domain = get_current_site(request).domain
        #domain = 'localhost:8000'
        domain = settings.HOST_ADDR
        uid = urlsafe_base64_encode(force_bytes(obj_pk))
        token = account_activation_token.make_token(user)
        email_subject = 'University Library - Activate your Student Account'
        email_body = render_to_string('librarymanagement/student/email_activation.html', {
                        'updated': user,
                        'domain': domain,
                        'uid':uid,
                        'token':token,
                    })
        recipient = (i,)
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