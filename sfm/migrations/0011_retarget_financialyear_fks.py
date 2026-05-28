from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Retarget sfm FK fields (SFMMetric.fy, Quarter.fy) from sfm.FinancialYear to ibms.FinancialYear
    (state only). The DB columns are unchanged.
    """

    dependencies = [
        ("sfm", "0010_remove_financialyear"),
        ("ibms", "0028_retarget_financialyear_fks"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="sfmmetric",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="quarter",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
