# Generated by Django 5.2.2 on 2025-06-13 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ibms', '0020_ibmdata_modified_ibmdata_modifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ibmdata',
            name='ibmIdentifier',
            field=models.CharField(db_index=True, max_length=100, verbose_name='IBM identifer'),
        ),
    ]
