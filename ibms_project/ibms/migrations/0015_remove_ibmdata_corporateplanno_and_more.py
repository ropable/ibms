# Generated by Django 4.2.16 on 2024-10-25 02:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ibms', '0014_auto_20230808_0743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ibmdata',
            name='corporatePlanNo',
        ),
        migrations.RemoveField(
            model_name='ibmdata',
            name='strategicPlanNo',
        ),
    ]
