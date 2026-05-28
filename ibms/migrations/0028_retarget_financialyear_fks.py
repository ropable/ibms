from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Retarget all ibms FK fields from sfm.FinancialYear to ibms.FinancialYear (state only).
    The DB table and columns are unchanged — the physical FK still points to sfm_financialyear,
    which ibms.FinancialYear is also using (via db_table) until migration 0029 renames it.
    """

    dependencies = [
        ("ibms", "0027_add_financialyear"),
        ("sfm", "0010_remove_financialyear"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="ibmdata",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="departmentprogram",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="glpivdownload",
                    name="fy",
                    field=models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="corporatestrategy",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="ncstrategicplan",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="generalservicepriority",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="ncservicepriority",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="pvsservicepriority",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="sfmservicepriority",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="erservicepriority",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="outcome",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
                migrations.AlterField(
                    model_name="serviceprioritymapping",
                    name="fy",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ibms.financialyear",
                        verbose_name="financial year",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
