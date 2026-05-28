from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Transfer FinancialYear model ownership from sfm to ibms (state only).
    The DB table sfm_financialyear already exists — no DB operations are needed here.
    """

    dependencies = [
        ("ibms", "0026_remove_erservicepriority_ibmdata_and_more"),
        ("sfm", "0009_auto_20210913_0858"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="FinancialYear",
                    fields=[
                        (
                            "financialYear",
                            models.CharField(
                                max_length=10,
                                primary_key=True,
                                serialize=False,
                                verbose_name="financial year",
                            ),
                        ),
                    ],
                    options={
                        "ordering": ("financialYear",),
                        "db_table": "sfm_financialyear",
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
