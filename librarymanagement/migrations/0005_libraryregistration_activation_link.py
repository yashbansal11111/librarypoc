# Generated by Django 4.0.4 on 2022-04-29 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarymanagement', '0004_alter_student_activation_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryregistration',
            name='activation_link',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]
