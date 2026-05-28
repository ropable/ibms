from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ibms", "0029_rename_financialyear_table"),
    ]

    operations = [
        # FinancialYear
        migrations.RenameField(model_name="financialyear", old_name="financialYear", new_name="financial_year"),
        # IBMData
        migrations.RenameField(model_name="ibmdata", old_name="ibmIdentifier", new_name="ibm_identifier"),
        migrations.RenameField(model_name="ibmdata", old_name="costCentre", new_name="cost_centre"),
        migrations.RenameField(model_name="ibmdata", old_name="budgetArea", new_name="budget_area"),
        migrations.RenameField(model_name="ibmdata", old_name="projectSponsor", new_name="project_sponsor"),
        migrations.RenameField(model_name="ibmdata", old_name="regionalSpecificInfo", new_name="regional_specific_info"),
        migrations.RenameField(model_name="ibmdata", old_name="servicePriorityID", new_name="service_priority_id"),
        migrations.RenameField(model_name="ibmdata", old_name="annualWPInfo", new_name="annual_wp_info"),
        migrations.RenameField(model_name="ibmdata", old_name="priorityActionNo", new_name="priority_action_no"),
        migrations.RenameField(model_name="ibmdata", old_name="priorityLevel", new_name="priority_level"),
        migrations.RenameField(model_name="ibmdata", old_name="marineKPI", new_name="marine_kpi"),
        migrations.RenameField(model_name="ibmdata", old_name="regionProject", new_name="region_project"),
        migrations.RenameField(model_name="ibmdata", old_name="regionDescription", new_name="region_description"),
        # DepartmentProgram
        migrations.RenameField(model_name="departmentprogram", old_name="ibmIdentifier", new_name="ibm_identifier"),
        # GLPivDownload
        migrations.RenameField(model_name="glpivdownload", old_name="costCentre", new_name="cost_centre"),
        migrations.RenameField(model_name="glpivdownload", old_name="regionBranch", new_name="region_branch"),
        migrations.RenameField(model_name="glpivdownload", old_name="downloadPeriod", new_name="download_period_str"),
        migrations.RenameField(model_name="glpivdownload", old_name="shortCode", new_name="short_code"),
        migrations.RenameField(model_name="glpivdownload", old_name="shortCodeName", new_name="short_code_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="gLCode", new_name="gl_code"),
        migrations.RenameField(model_name="glpivdownload", old_name="ptdActual", new_name="ptd_actual"),
        migrations.RenameField(model_name="glpivdownload", old_name="ptdBudget", new_name="ptd_budget"),
        migrations.RenameField(model_name="glpivdownload", old_name="ytdActual", new_name="ytd_actual"),
        migrations.RenameField(model_name="glpivdownload", old_name="ytdBudget", new_name="ytd_budget"),
        migrations.RenameField(model_name="glpivdownload", old_name="ytdVariance", new_name="ytd_variance"),
        migrations.RenameField(model_name="glpivdownload", old_name="ccName", new_name="cc_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="serviceName", new_name="service_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="activityName", new_name="activity_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="resourceName", new_name="resource_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="projectName", new_name="project_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="jobName", new_name="job_name"),
        migrations.RenameField(model_name="glpivdownload", old_name="codeID", new_name="code_id"),
        migrations.RenameField(model_name="glpivdownload", old_name="resNameNo", new_name="res_name_no"),
        migrations.RenameField(model_name="glpivdownload", old_name="actNameNo", new_name="act_name_no"),
        migrations.RenameField(model_name="glpivdownload", old_name="projNameNo", new_name="proj_name_no"),
        migrations.RenameField(model_name="glpivdownload", old_name="resourceCategory", new_name="resource_category"),
        migrations.RenameField(model_name="glpivdownload", old_name="expenseRevenue", new_name="expense_revenue"),
        migrations.RenameField(model_name="glpivdownload", old_name="fireActivities", new_name="fire_activities"),
        migrations.RenameField(model_name="glpivdownload", old_name="mPRACategory", new_name="mpra_category"),
        # CorporateStrategy
        migrations.RenameField(model_name="corporatestrategy", old_name="corporateStrategyNo", new_name="corporate_strategy_no"),
        # NCStrategicPlan
        migrations.RenameField(model_name="ncstrategicplan", old_name="strategicPlanNo", new_name="strategic_plan_no"),
        migrations.RenameField(model_name="ncstrategicplan", old_name="directionNo", new_name="direction_no"),
        migrations.RenameField(model_name="ncstrategicplan", old_name="aimNo", new_name="aim_no"),
        migrations.RenameField(model_name="ncstrategicplan", old_name="actionNo", new_name="action_no"),
        # GeneralServicePriority (inherits ServicePriority abstract fields)
        migrations.RenameField(model_name="generalservicepriority", old_name="categoryID", new_name="category_id"),
        migrations.RenameField(model_name="generalservicepriority", old_name="servicePriorityNo", new_name="service_priority_no"),
        migrations.RenameField(model_name="generalservicepriority", old_name="strategicPlanNo", new_name="strategic_plan_no"),
        migrations.RenameField(model_name="generalservicepriority", old_name="corporateStrategyNo", new_name="corporate_strategy_no"),
        migrations.RenameField(model_name="generalservicepriority", old_name="pvsExampleAnnWP", new_name="pvs_example_ann_wp"),
        migrations.RenameField(model_name="generalservicepriority", old_name="pvsExampleActNo", new_name="pvs_example_act_no"),
        # NCServicePriority (inherits ServicePriority abstract fields + own fields)
        migrations.RenameField(model_name="ncservicepriority", old_name="categoryID", new_name="category_id"),
        migrations.RenameField(model_name="ncservicepriority", old_name="servicePriorityNo", new_name="service_priority_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="strategicPlanNo", new_name="strategic_plan_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="corporateStrategyNo", new_name="corporate_strategy_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="pvsExampleAnnWP", new_name="pvs_example_ann_wp"),
        migrations.RenameField(model_name="ncservicepriority", old_name="pvsExampleActNo", new_name="pvs_example_act_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="assetNo", new_name="asset_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="targetNo", new_name="target_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="actionNo", new_name="action_no"),
        migrations.RenameField(model_name="ncservicepriority", old_name="mileNo", new_name="mile_no"),
        # PVSServicePriority (inherits ServicePriority abstract fields + own fields)
        migrations.RenameField(model_name="pvsservicepriority", old_name="categoryID", new_name="category_id"),
        migrations.RenameField(model_name="pvsservicepriority", old_name="servicePriorityNo", new_name="service_priority_no"),
        migrations.RenameField(model_name="pvsservicepriority", old_name="strategicPlanNo", new_name="strategic_plan_no"),
        migrations.RenameField(model_name="pvsservicepriority", old_name="corporateStrategyNo", new_name="corporate_strategy_no"),
        migrations.RenameField(model_name="pvsservicepriority", old_name="pvsExampleAnnWP", new_name="pvs_example_ann_wp"),
        migrations.RenameField(model_name="pvsservicepriority", old_name="pvsExampleActNo", new_name="pvs_example_act_no"),
        migrations.RenameField(model_name="pvsservicepriority", old_name="servicePriority1", new_name="service_priority_1"),
        # SFMServicePriority (inherits ServicePriority abstract fields + own fields)
        migrations.RenameField(model_name="sfmservicepriority", old_name="categoryID", new_name="category_id"),
        migrations.RenameField(model_name="sfmservicepriority", old_name="servicePriorityNo", new_name="service_priority_no"),
        migrations.RenameField(model_name="sfmservicepriority", old_name="strategicPlanNo", new_name="strategic_plan_no"),
        migrations.RenameField(model_name="sfmservicepriority", old_name="corporateStrategyNo", new_name="corporate_strategy_no"),
        migrations.RenameField(model_name="sfmservicepriority", old_name="pvsExampleAnnWP", new_name="pvs_example_ann_wp"),
        migrations.RenameField(model_name="sfmservicepriority", old_name="pvsExampleActNo", new_name="pvs_example_act_no"),
        migrations.RenameField(model_name="sfmservicepriority", old_name="regionBranch", new_name="region_branch"),
        # ERServicePriority (inherits ServicePriority abstract fields only)
        migrations.RenameField(model_name="erservicepriority", old_name="categoryID", new_name="category_id"),
        migrations.RenameField(model_name="erservicepriority", old_name="servicePriorityNo", new_name="service_priority_no"),
        migrations.RenameField(model_name="erservicepriority", old_name="strategicPlanNo", new_name="strategic_plan_no"),
        migrations.RenameField(model_name="erservicepriority", old_name="corporateStrategyNo", new_name="corporate_strategy_no"),
        migrations.RenameField(model_name="erservicepriority", old_name="pvsExampleAnnWP", new_name="pvs_example_ann_wp"),
        migrations.RenameField(model_name="erservicepriority", old_name="pvsExampleActNo", new_name="pvs_example_act_no"),
        # Outcome
        migrations.RenameField(model_name="outcome", old_name="q1Input", new_name="q1_input"),
        migrations.RenameField(model_name="outcome", old_name="q2Input", new_name="q2_input"),
        migrations.RenameField(model_name="outcome", old_name="q3Input", new_name="q3_input"),
        migrations.RenameField(model_name="outcome", old_name="q4Input", new_name="q4_input"),
        # ServicePriorityMapping
        migrations.RenameField(model_name="serviceprioritymapping", old_name="costCentreNo", new_name="cost_centre_no"),
        migrations.RenameField(model_name="serviceprioritymapping", old_name="wildlifeManagement", new_name="wildlife_management"),
        migrations.RenameField(model_name="serviceprioritymapping", old_name="parksManagement", new_name="parks_management"),
        migrations.RenameField(model_name="serviceprioritymapping", old_name="forestManagement", new_name="forest_management"),
    ]
