# Generated by Django 4.0.4 on 2022-05-12 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarymanagement', '0017_remove_issuebook_select_no_of_weeks_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuebook',
            name='select_no_of_days',
            field=models.IntegerField(default=7, null=True),
        ),
    ]
