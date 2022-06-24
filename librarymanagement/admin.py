from django.contrib import admin
from django.contrib.auth.models import Group
from librarymanagement.models import IssueBook, LibraryRegistration, Student, BookData, Staff


# Register your models here.

class LibraryRegistrationAdmin(admin.ModelAdmin):
    """This is a class for defining what to display from LibraryRegistration model/
       on the admin page of this model"""
    list_display=('username','is_staff','is_active','is_initial','is_invited','open_link')
    ordering=('username',)
    search_fields = ('first_name',)

class StudentAdmin(admin.ModelAdmin):
    """This is a class for defining what to display from Student model/
       on the admin page of this model"""
    list_display=('email','is_active','is_initial','is_invited','open_link')
    ordering=('email',)
    search_fields = ('first_name',)

class BookAdmin(admin.ModelAdmin):
    """This is a class for defining what to display from BookData model/
       on the admin page of this model"""
    list_display = ('bookname', 'quantity')
    ordering = ('bookname',)
    search_fields = ('bookname',)

class IssueBookAdmin(admin.ModelAdmin):
    """This is a class for defining what to display from IssueBook model/
       on the admin page of this model"""
    list_display = ('username',
                    'select_book',
                    'is_pending',
                    'is_approved',
                    'is_rejected',
                    'is_returned'
                    )
    ordering = ('username',)
    search_fields = ('username',)

class StaffAdmin(admin.ModelAdmin):
    """This is a class for defining what to display from Student model/
       on the admin page of this model"""
    list_display=('email','is_active','is_initial','is_invited','open_link')
    ordering=('email',)
    search_fields = ('first_name',)

admin.site.register(Student, StudentAdmin)
admin.site.unregister(Group)
admin.site.register(LibraryRegistration, LibraryRegistrationAdmin)
admin.site.register(BookData, BookAdmin)
admin.site.register(IssueBook, IssueBookAdmin)
admin.site.register(Staff, StaffAdmin)
