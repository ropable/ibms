# Generated by Django 3.2.20 on 2023-08-02 01:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sfm', '0009_auto_20210913_0858'),
        ('ibms', '0013_glpivdownload_download_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='ibmdata',
            name='marineKMI',
            field=models.TextField(null=True, verbose_name='marine KPI'),
        ),
        migrations.AddField(
            model_name='ibmdata',
            name='priorityActionNo',
            field=models.TextField(null=True, verbose_name='priority action no'),
        ),
        migrations.AddField(
            model_name='ibmdata',
            name='priorityLevel',
            field=models.TextField(null=True, verbose_name='priority level'),
        ),
        migrations.AddField(
            model_name='ibmdata',
            name='regionDescription',
            field=models.TextField(null=True, verbose_name='region description'),
        ),
        migrations.AddField(
            model_name='ibmdata',
            name='regionProject',
            field=models.TextField(null=True, verbose_name='region project'),
        ),
        migrations.AlterField(
            model_name='corporatestrategy',
            name='corporateStrategyNo',
            field=models.CharField(max_length=100, verbose_name='corporate strategy no'),
        ),
        migrations.AlterField(
            model_name='corporatestrategy',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='erservicepriority',
            name='categoryID',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='category ID'),
        ),
        migrations.AlterField(
            model_name='erservicepriority',
            name='corporateStrategyNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='corporate strategy no'),
        ),
        migrations.AlterField(
            model_name='erservicepriority',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='erservicepriority',
            name='servicePriorityNo',
            field=models.CharField(db_index=True, default='-1', max_length=100, verbose_name='service priority no'),
        ),
        migrations.AlterField(
            model_name='erservicepriority',
            name='strategicPlanNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='strategic plan no'),
        ),
        migrations.AlterField(
            model_name='generalservicepriority',
            name='categoryID',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='category ID'),
        ),
        migrations.AlterField(
            model_name='generalservicepriority',
            name='corporateStrategyNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='corporate strategy no'),
        ),
        migrations.AlterField(
            model_name='generalservicepriority',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='generalservicepriority',
            name='servicePriorityNo',
            field=models.CharField(db_index=True, default='-1', max_length=100, verbose_name='service priority no'),
        ),
        migrations.AlterField(
            model_name='generalservicepriority',
            name='strategicPlanNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='strategic plan no'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='activityName',
            field=models.CharField(max_length=100, verbose_name='activity name'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='ccName',
            field=models.CharField(max_length=100, verbose_name='CC name'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='codeID',
            field=models.CharField(db_index=True, help_text="This should match an IBMData object's IBMIdentifier field.", max_length=30, verbose_name='code ID'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='costCentre',
            field=models.CharField(db_index=True, max_length=4, verbose_name='cost centre'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='expenseRevenue',
            field=models.CharField(max_length=7, verbose_name='expense revenue'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='fireActivities',
            field=models.CharField(max_length=50, verbose_name='fire activities'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='gLCode',
            field=models.CharField(max_length=30, verbose_name='GL code'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='jobName',
            field=models.CharField(max_length=100, verbose_name='job name'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='projectName',
            field=models.CharField(max_length=100, verbose_name='project name'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='regionBranch',
            field=models.CharField(db_index=True, max_length=100, verbose_name='region branch'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='resourceCategory',
            field=models.CharField(max_length=100, verbose_name='resource category'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='resourceName',
            field=models.CharField(max_length=100, verbose_name='resource name'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='serviceName',
            field=models.CharField(max_length=100, verbose_name='service name'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='shortCode',
            field=models.CharField(max_length=20, verbose_name='short code'),
        ),
        migrations.AlterField(
            model_name='glpivdownload',
            name='shortCodeName',
            field=models.CharField(max_length=200, verbose_name='short code name'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='annualWPInfo',
            field=models.TextField(verbose_name='annual WP info'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='budgetArea',
            field=models.CharField(db_index=True, max_length=100, verbose_name='budget area'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='corporatePlanNo',
            field=models.CharField(db_index=True, max_length=100, verbose_name='corporate plan no'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='costCentre',
            field=models.CharField(blank=True, db_index=True, max_length=4, null=True, verbose_name='cost centre'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='ibmIdentifier',
            field=models.CharField(max_length=100, verbose_name='IBM identifer'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='projectSponsor',
            field=models.CharField(db_index=True, max_length=100, verbose_name='project sponsor'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='regionalSpecificInfo',
            field=models.TextField(verbose_name='regional specific info'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='servicePriorityID',
            field=models.CharField(max_length=100, verbose_name='service priority ID'),
        ),
        migrations.AlterField(
            model_name='ibmdata',
            name='strategicPlanNo',
            field=models.CharField(db_index=True, max_length=100, verbose_name='strategic plan no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='actionNo',
            field=models.CharField(max_length=30, verbose_name='action no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='assetNo',
            field=models.CharField(max_length=5, verbose_name='asset no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='categoryID',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='category ID'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='corporateStrategyNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='corporate strategy no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='mileNo',
            field=models.CharField(max_length=30, verbose_name='mile no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='servicePriorityNo',
            field=models.CharField(db_index=True, default='-1', max_length=100, verbose_name='service priority no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='strategicPlanNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='strategic plan no'),
        ),
        migrations.AlterField(
            model_name='ncservicepriority',
            name='targetNo',
            field=models.CharField(max_length=30, verbose_name='target no'),
        ),
        migrations.AlterField(
            model_name='ncstrategicplan',
            name='ActionNo',
            field=models.TextField(verbose_name='action no'),
        ),
        migrations.AlterField(
            model_name='ncstrategicplan',
            name='AimNo',
            field=models.CharField(max_length=100, verbose_name='aim no'),
        ),
        migrations.AlterField(
            model_name='ncstrategicplan',
            name='directionNo',
            field=models.CharField(max_length=100, verbose_name='direction no'),
        ),
        migrations.AlterField(
            model_name='ncstrategicplan',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='ncstrategicplan',
            name='strategicPlanNo',
            field=models.CharField(max_length=100, verbose_name='strategic plan no'),
        ),
        migrations.AlterField(
            model_name='outcomes',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='pvsservicepriority',
            name='categoryID',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='category ID'),
        ),
        migrations.AlterField(
            model_name='pvsservicepriority',
            name='corporateStrategyNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='corporate strategy no'),
        ),
        migrations.AlterField(
            model_name='pvsservicepriority',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='pvsservicepriority',
            name='servicePriority1',
            field=models.TextField(verbose_name='service priority 1'),
        ),
        migrations.AlterField(
            model_name='pvsservicepriority',
            name='servicePriorityNo',
            field=models.CharField(db_index=True, default='-1', max_length=100, verbose_name='service priority no'),
        ),
        migrations.AlterField(
            model_name='pvsservicepriority',
            name='strategicPlanNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='strategic plan no'),
        ),
        migrations.AlterField(
            model_name='serviceprioritymappings',
            name='costCentreNo',
            field=models.CharField(max_length=4, verbose_name='cost centre no'),
        ),
        migrations.AlterField(
            model_name='serviceprioritymappings',
            name='forestManagement',
            field=models.CharField(max_length=100, verbose_name='forest management'),
        ),
        migrations.AlterField(
            model_name='serviceprioritymappings',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='serviceprioritymappings',
            name='parksManagement',
            field=models.CharField(max_length=100, verbose_name='parks management'),
        ),
        migrations.AlterField(
            model_name='serviceprioritymappings',
            name='wildlifeManagement',
            field=models.CharField(max_length=100, verbose_name='wildlife management'),
        ),
        migrations.AlterField(
            model_name='sfmservicepriority',
            name='categoryID',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='category ID'),
        ),
        migrations.AlterField(
            model_name='sfmservicepriority',
            name='corporateStrategyNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='corporate strategy no'),
        ),
        migrations.AlterField(
            model_name='sfmservicepriority',
            name='fy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sfm.financialyear', verbose_name='financial year'),
        ),
        migrations.AlterField(
            model_name='sfmservicepriority',
            name='regionBranch',
            field=models.CharField(max_length=20, verbose_name='region branch'),
        ),
        migrations.AlterField(
            model_name='sfmservicepriority',
            name='servicePriorityNo',
            field=models.CharField(db_index=True, default='-1', max_length=100, verbose_name='service priority no'),
        ),
        migrations.AlterField(
            model_name='sfmservicepriority',
            name='strategicPlanNo',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='strategic plan no'),
        ),
    ]
