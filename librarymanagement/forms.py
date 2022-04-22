from django import forms
from librarymanagement.models import BookData, IssueBook, LibraryRegistration


# class LibraryRegisterForm(forms.ModelForm):
#     email = forms.EmailField(label = ("E-mail Address"),required=True)
#     #password1 = forms.CharField(label = ("Password"),widget=forms.PasswordInput, required=True)
#     #password2 = forms.CharField(label = ("Password Confirmation"),
#     #                            widget=forms.PasswordInput,
#     #                            required=True
#     #                            )
#     class Meta:
#         model = Student
#         #fields = ['email','password1', 'password2']
#         fields = ['email']


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
    username = forms.EmailField(label = ("Email-address"),required=True,disabled=True)
    password1 = forms.CharField(label = ("Password"),widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label = ("Password Confirmation"),
                                widget=forms.PasswordInput,
                                required=True
                                )
    class Meta:
        """This is Meta class """
        model = LibraryRegistration
        fields = ['username','password1', 'password2']

    def __init__(self, instance):
        super().__init__()
        self.fields['username'].initial = instance

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
    class Meta:
        """This is Meta Class"""
        model = BookData
        fields = '__all__'

class StaffForm(forms.ModelForm):
    """This is form class for Staff"""
    username = forms.EmailField(label = ("Email-address"),required=True)
    first_name = forms.CharField(max_length=100, label = ('First Name'), required=True)
    last_name = forms.CharField(max_length=100, label = ('Last Name'), required=True)
    phone_no = forms.IntegerField(label = ('Contact Number'), required=True)
    class Meta:
        """This is Meta Class"""
        model = LibraryRegistration
        fields = ['username', 'first_name', 'last_name','phone_no']
        