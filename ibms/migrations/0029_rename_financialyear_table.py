from django.db import migrations


class Migration(migrations.Migration):
    """
    Rename the DB table from sfm_financialyear to ibms_financialyear now that all FK state
    references have been retargeted to ibms.FinancialYear.
    """

    dependencies = [
        ("ibms", "0028_retarget_financialyear_fks"),
        ("sfm", "0011_retarget_financialyear_fks"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="financialyear",
            table="ibms_financialyear",
        ),
    ]
