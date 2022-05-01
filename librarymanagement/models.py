from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


class Student(models.Model):
    """This is model class for Student table"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(validators=[MaxValueValidator(limit_value=date.today)],
                                     default=None
                                     )
    email = models.EmailField(max_length=100, unique=True)
    phone = models.BigIntegerField(validators=[MaxValueValidator(9999999999),
                                               MinValueValidator(1000000000)
                                               ],
                                   unique=True
                                   )
    is_active = models.BooleanField(default=False,
                                    help_text='Designates whether this user\
                                               should be treated as active. \
                                               Unselect this instead of deleting accounts.',
                                    verbose_name='active')
    is_invited = models.BooleanField(default=False,
                                     help_text='Designates whether this user\
                                                has received activation link on its email',
                                     verbose_name='Invited'
                                     )
    is_initial = models.BooleanField(default=True,
                                     help_text='Designates whether this user\
                                                is newly created and its\
                                                email activation is still pending',
                                     verbose_name='Initial'
                                     )
    open_link = models.BooleanField(default=False,
                                    help_text='Designates whether this user\
                                               has clicked on activation link\
                                               sent on his/her email',
                                    verbose_name='Opened Link'
                                    )
    activation_link = models.CharField(max_length=200, default=None, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name', 'date_of_birth', 'email', 'phone']

    def __str__(self):
        return str(self.email)


class LibraryRegistration(AbstractUser):
    """This is model class for Student Registration"""
    phone = models.BigIntegerField(validators=[MaxValueValidator(9999999999),
                                                  MinValueValidator(1000000000)],
                                      unique=True,
                                      null=True
                                      )
    is_initial = models.BooleanField(default=False,
                                     help_text='Designates whether this user\
                                                is newly created and its\
                                                email activation is still pending',
                                     verbose_name='Initial'
                                     )
    is_invited = models.BooleanField(default=False,
                                     help_text='Designates whether this user\
                                                has received activation link on its email',
                                     verbose_name='Invited'
                                     )
    open_link = models.BooleanField(default=False,
                                    help_text='Designates whether this user\
                                               has clicked on activation link\
                                               sent on his/her email',
                                    verbose_name='Opened Link'
                                    )
    activation_link = models.CharField(max_length=200, default=None, null=True)
    def __str__(self):
        return str(self.username)


class BookData(models.Model):
    """This is model class for Books Table"""
    bookname = models.CharField(max_length=100)
    quantity = models.IntegerField(default = 0)

    def __str__(self):
        return str(self.bookname)


class IssueBook(models.Model):
    """This is model class for Books Issued by Students"""
    username = models.ForeignKey(LibraryRegistration, on_delete=models.CASCADE, default = None)
    select_book = models.ForeignKey(BookData, on_delete=models.DO_NOTHING)
    issue_date = models.DateField()
    return_date = models.DateField(null=True)
    select_no_of_weeks = models.CharField(max_length = 10,choices = (('1','One Week'),
                                                                     ('2','Two Weeks'),
                                                                     ('3', 'Three Weeks'),
                                                                     ('4', 'Four Weeks')
                                                                     ),
                                                                     null=True )

    def __str__(self):
        return str(self.username)
