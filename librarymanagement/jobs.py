from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from librarymanagement.models import LibraryRegistration
from .tokens import account_activation_token
from django.conf import settings

def checkinitial():

    obj = list(LibraryRegistration.objects.filter(is_initial = True))
    print(obj)

    for i in obj:
        user = LibraryRegistration.objects.get(username = i)
        pk_obj = user.pk

        #domain = get_current_site(request).domain
        #domain = 'localhost:8000'
        domain = settings.HOST_ADDR
        email_subject = 'University Library - Activate your Staff Account'
        email_body = render_to_string('librarymanagement/staff_email_activation.html', {
                        'updated': user,
                        'domain': domain,
                        'uid':urlsafe_base64_encode(force_bytes(pk_obj)),
                        'token':account_activation_token.make_token(user),
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
        user.is_initial = False
        user.is_invited = True
        user.save()
        