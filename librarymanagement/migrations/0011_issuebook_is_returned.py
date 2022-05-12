# Generated by Django 4.0.4 on 2022-05-08 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarymanagement', '0010_alter_issuebook_issue_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuebook',
            name='is_returned',
            field=models.BooleanField(default=False, help_text='Designates whether your issued book is                                                returned or not', verbose_name='Book Returned'),
        ),
    ]
