# Generated by Django 4.0.4 on 2022-04-28 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarymanagement', '0002_student_activation_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='activation_link',
            field=models.CharField(default=None, max_length=200),
        ),
    ]
