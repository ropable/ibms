from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove FinancialYear from sfm's migration state now that ibms owns it.
    The DB table is unchanged — no DB operations are needed here.
    """

    dependencies = [
        ("sfm", "0009_auto_20210913_0858"),
        ("ibms", "0027_add_financialyear"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel("FinancialYear"),
            ],
            database_operations=[],
        ),
    ]
