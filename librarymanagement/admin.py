from django.contrib import admin
from django.contrib.auth.models import Group
from librarymanagement.models import IssueBook, LibraryRegistration, Student, BookData


# Register your models here.

admin.site.register(Student)
admin.site.unregister(Group)
admin.site.register(LibraryRegistration)
admin.site.register(BookData)
admin.site.register(IssueBook)
