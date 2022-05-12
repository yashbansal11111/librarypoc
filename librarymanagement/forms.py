from django import forms
from django.conf import settings
from librarymanagement.models import BookData, IssueBook, LibraryRegistration, Student


class PasswordForm(forms.ModelForm):
    """This is Form class for Password Generation"""
    email_address = forms.EmailField(required=True,disabled=True)
    password1 = forms.CharField(label = ("Password"),widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label = ("Password Confirmation"),
                                widget=forms.PasswordInput,
                                required=True
                                )
    class Meta:
        """This is Meta class """
        model = LibraryRegistration
        fields = ['email_address','password1', 'password2']

    def __init__(self, instance):
        super().__init__()
        self.fields['email_address'].initial = instance

class StaffPasswordForm(forms.ModelForm):
    """This is Form class for Password Generation"""
    email_address = forms.EmailField(required=True,disabled=True)
    password1 = forms.CharField(label = ("Password"),widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label = ("Password Confirmation"),
                                widget=forms.PasswordInput,
                                required=True
                                )
    class Meta:
        """This is Meta class """
        model = LibraryRegistration
        fields = ['email_address','password1', 'password2']

    def __init__(self, instance):
        super().__init__()
        self.fields['email_address'].initial = instance

class LoginForm(forms.ModelForm):
    """This is Form class for Student Login"""
    username = forms.EmailField(label = ("Email-Address"),required = True)
    password1 = forms.CharField(label = ('Password'), widget = forms.PasswordInput, required=True)
    class Meta:
        """This is Meta class """
        model = LibraryRegistration
        fields = ['username', 'password1']


class IssueBookForm(forms.ModelForm):
    """This is Form class for Issuing Book to Students"""
    class Meta:
        """This is Meta class """
        model = IssueBook
        fields = ['select_book', 'select_no_of_weeks']

class BookDataForm(forms.ModelForm):
    """This is Form class for Book Database"""
    bookname = forms.CharField(widget = forms.TextInput(attrs={'placeholder':'Enter a bookname...'}),
                               required=True)
    quantity = forms.IntegerField(required=True)
    class Meta:
        """This is Meta Class"""
        model = BookData
        fields = '__all__'

class EntryForm(forms.ModelForm):
    """This is form class for Staff entry by admin"""
    username = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':'Enter Email-Address'}),
                                label = ("Email-address"),
                                required=True
                                )
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter First Name'}),
                                 max_length=100,
                                 label = ('First Name'),
                                 required=True
                                 )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Last Name'}),
                                max_length=100,
                                label = ('Last Name'),
                                required=True
                                )
    phone = forms.IntegerField(widget=forms.TextInput(
                               attrs={'placeholder':'Enter 10 digit mobile no.'}),
                               label = ('Contact Number'),
                               required=True
                               )
    class Meta:
        """This is Meta Class"""
        model = LibraryRegistration
        fields = ['first_name', 'last_name','username','phone']

class StudentEntryForm(forms.ModelForm):
    """This is form class for Student entry by admin"""
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter First Name'}),
                                 max_length=100,
                                 label = ('First Name'),
                                 required=True
                                 )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Last Name'}),
                                max_length=100,
                                label = ('Last Name'),
                                required=True
                                )
    date_of_birth = forms.DateField(widget=forms.DateInput(format=settings.DATE_INPUT_FORMATS,
                                                           attrs={'class': 'datepicker',
                                                                  'type': 'date',
                                                                  'placeholder':'Select a Date'
                                                                  }
                                                           )
                                    )
    username = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':'Enter Email-Address'}),
                                label = ("Email-address"),
                                required=True
                                )
    phone = forms.IntegerField(widget=forms.TextInput(
                               attrs={'placeholder':'Enter 10 digit mobile no.'}),
                               label = ('Contact Number'),
                               required=True
                               )
    class Meta:
        """This is Meta Class"""
        model = Student
        fields = ['first_name', 'last_name','date_of_birth','username','phone']

class PasswordResetForm(forms.ModelForm):
    """This is a form for reset password main page"""
    username = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':'Enter Email-Address'}),
                                label = ("Email"),
                                required=True
                                )
    class Meta:
        """This is Meta Class"""
        model = LibraryRegistration
        fields = ['username']

class ExistingUserPassResetForm(forms.ModelForm):
    """This is a form for resetting password for existing users."""
    password1 = forms.CharField(label = ('Enter Current Password'), widget = forms.PasswordInput(attrs={'placeholder':'Enter Current Password'}), required=True)
    password2 = forms.CharField(label = ('Enter New Password'), widget = forms.PasswordInput(attrs={'placeholder':'Enter New Password'}), required=True)
    password3 = forms.CharField(label = ('Confirm New Password'), widget = forms.PasswordInput(attrs={'placeholder':'Re-enter New Password','autocomplete': 'off','data-toggle': 'password'}), required=True)
    class Meta:
        """This is Meta Class"""
        model = LibraryRegistration
        fields = ['password1', 'password2', 'password3']

class StudentEditForm(forms.ModelForm):
    """This is form class for Student entry by admin"""
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter First Name'}),
                                 max_length=100,
                                 label = ('First Name'),
                                 required=True
                                 )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Last Name'}),
                                max_length=100,
                                label = ('Last Name'),
                                required=True
                                )
    date_of_birth = forms.DateField(widget=forms.DateInput(format=settings.DATE_INPUT_FORMATS,
                                                           attrs={'class': 'datepicker',
                                                                  'type': 'date',
                                                                  'placeholder':'Select a Date'
                                                                  }
                                                           )
                                    )
    phone = forms.IntegerField(widget=forms.TextInput(
                               attrs={'placeholder':'Enter 10 digit mobile no.'}),
                               label = ('Contact Number'),
                               required=True
                               )
    is_active = forms.BooleanField(label = ("Active Status"), required=False)
    class Meta:
        """This is Meta Class"""
        model = Student
        fields = ['first_name', 'last_name','date_of_birth','phone','is_active']
