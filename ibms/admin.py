import csv
import logging
from typing import List, Optional

from django import forms
from django.contrib.admin import ModelAdmin, register
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from .models import (
    CorporateStrategy,
    DepartmentProgram,
    ERServicePriority,
    FinancialYear,
    GeneralServicePriority,
    GLPivDownload,
    IBMData,
    NCServicePriority,
    NCStrategicPlan,
    PVSServicePriority,
    ServicePriorityMapping,
    SFMServicePriority,
)

LOGGER = logging.getLogger("ibms")


def export_as_csv_action(
    fields: Optional[List[str]] = None,
    translations: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    header: bool = True,
    description: str = "Export selected objects to CSV",
):
    """
    This function adds an "Export as CSV" action to a model in the Django admin site.
    Register the action using the ModelAdmin ``action`` option.
    ``fields`` and ``exclude`` work the same as those Django ModelForm options (use one or the other).
    ``header`` defines whether or not the column names are output as the first row.
    """

    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        """
        # Basic audit logging.
        LOGGER.info(f"{queryset.model._meta.verbose_name} CSV export by {request.user.username}: {queryset.count()} records")
        field_names = [field.name for field in modeladmin.model._meta.fields]
        if fields:
            field_names = fields
        elif exclude:
            excludeset = set(exclude)
            field_names = [f for f in field_names if f not in excludeset]
        # Create the response object.
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=ibms_{modeladmin.model._meta.model_name}.csv"
        writer = csv.writer(response)
        if header:
            writer.writerow(list(translations))
        else:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = description
    return export_as_csv


@register(FinancialYear)
class FinancialYearAdmin(ModelAdmin):
    search_fields = ["financial_year"]
    list_display = ["financial_year"]
    list_filter = ["financial_year"]
    actions = [export_as_csv_action(translations=["financial_year"], fields=["financial_year"])]


@register(IBMData)
class IBMDataAdmin(VersionAdmin):
    date_hierarchy = "modified"
    search_fields = ("fy__financial_year", "ibm_identifier", "budget_area", "modifier__username")
    list_display = ("ibm_identifier", "fy", "cost_centre", "budget_area", "service_priority_link", "modified", "modifier")
    list_filter = ("fy__financial_year", "cost_centre", "budget_area", "service")
    ordering = ("ibm_identifier",)
    readonly_fields = (
        "fy",
        "ibm_identifier",
        "budget_area",
        "project_sponsor",
        "regional_specific_info",
        "service_priority_id",
        "annual_wp_info",
        "cost_centre",
        "account_display",
        "service",
        "activity",
        "project",
        "job",
        "priority_action_no",
        "priority_level",
        "marine_kpi",
        "region_project",
        "region_description",
        "modified",
        "modifier",
    )
    fieldsets = (
        (
            "IBM data record",
            {
                "fields": (
                    "fy",
                    "ibm_identifier",
                    "budget_area",
                    "project_sponsor",
                    "regional_specific_info",
                    "service_priority_id",
                    "annual_wp_info",
                    "cost_centre",
                    "account_display",
                    "service",
                    "activity",
                    "project_display",
                    "job_display",
                    "priority_action_no",
                    "priority_level",
                    "marine_kpi",
                    "region_project",
                    "region_description",
                )
            },
        ),
        ("Audit fields", {"fields": ("modified", "modifier")}),
    )
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "ibm_identifier",
                "cost_centre",
                "account",
                "service",
                "activity",
                "project",
                "job",
                "budget_area",
                "project_sponsor",
                "regional_specific_info",
                "service_priority_id",
                "annual_wp_info",
                "priority_action_no",
                "priority_level",
                "marine_kpi",
                "region_project",
                "region_description",
                "last modified by",
                "last modified",
            ],
            fields=[
                "fy",
                "ibm_identifier",
                "cost_centre",
                "account",
                "service",
                "activity",
                "project",
                "job",
                "budget_area",
                "project_sponsor",
                "regional_specific_info",
                "service_priority_id",
                "annual_wp_info",
                "priority_action_no",
                "priority_level",
                "marine_kpi",
                "region_project",
                "region_description",
                "modifier",
                "modified",
            ],
        )
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def account_display(self, obj):
        return obj.get_account_display()

    account_display.short_description = "account"

    def project_display(self, obj):
        return obj.get_project_display()

    project_display.short_description = "project"

    def job_display(self, obj):
        return obj.get_job_display()

    job_display.short_description = "job"

    def service_priority_link(self, obj):
        if obj.service_priority:
            named_url = f"admin:ibms_{obj.content_type.model}_change"
            url = reverse(named_url, args=[obj.object_id])
            return format_html(format_string=f"<a href='{url}'>{obj.service_priority.service_priority_no}</a>")
        else:
            return ""

    service_priority_link.short_description = "Service priority"


class DepartmentProgramAdminForm(forms.ModelForm):
    class Meta:
        model = DepartmentProgram
        fields = ["fy", "ibm_identifier", "dept_program1", "dept_program2", "dept_program3"]
        widgets = {
            "dept_program1": forms.Textarea(attrs={"cols": "80", "rows": "4"}),
            "dept_program2": forms.Textarea(attrs={"cols": "80", "rows": "4"}),
            "dept_program3": forms.Textarea(attrs={"cols": "80", "rows": "4"}),
        }


@register(DepartmentProgram)
class DepartmentProgramAdmin(ModelAdmin):
    form = DepartmentProgramAdminForm
    list_display = ["ibm_identifier", "fy", "dept_program1"]
    list_filter = [
        "fy__financial_year",
    ]
    fields = ["fy", "ibm_identifier", "dept_program1", "dept_program2", "dept_program3"]
    readonly_fields = ["fy", "ibm_identifier"]
    search_fields = ["ibm_identifier", "dept_program1", "dept_program2", "dept_program3"]
    actions = [
        export_as_csv_action(
            translations=["financial_year", "ibm_identifier", "DeptProgram1", "DeptProgram2", "DeptProgram3"],
            fields=["fy", "ibm_identifier", "dept_program1", "dept_program2", "dept_program3"],
        )
    ]


@register(GLPivDownload)
class GLPivDownloadAdmin(ModelAdmin):
    date_hierarchy = "download_period"
    search_fields = (
        "fy__financial_year",
        "cost_centre",
        "account",
        "service",
        "activity",
        "cc_name",
        "short_code",
        "short_code_name",
        "gl_code",
        "code_id",
    )
    list_display = (
        "gl_code",
        "fy",
        "division",
        "cc_name",
        "project_name",
        "ibmdata_link",
        "department_program_link",
    )
    list_filter = ("fy__financial_year", "division", "region_branch", "cost_centre")
    fields = (
        "fy",
        "cost_centre",
        "region_branch",
        "service",
        "project",
        "job",
        "download_period",
        "download_period_str",
        "account_display",
        "activity",
        "resource",
        "short_code",
        "short_code_name",
        "gl_code",
        "ptd_actual",
        "ptd_budget",
        "ytd_actual",
        "ytd_budget",
        "fybudget",
        "ytd_variance",
        "cc_name",
        "service_name",
        "activity_name",
        "resource_name",
        "project_name",
        "job_name",
        "code_id",
        "res_name_no",
        "act_name_no",
        "proj_name_no",
        "division",
        "resource_category",
        "wildfire",
        "expense_revenue",
        "fire_activities",
        "mpra_category",
    )
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "Download Period",
                "CC",
                "Account",
                "Service",
                "Activity",
                "Resource",
                "Project",
                "Job",
                "Shortcode",
                "Shortcode_Name",
                "GL_Code",
                "PTD_Actual",
                "PTD_Budget",
                "YTD_Actual",
                "YTD_Budget",
                "FY_Budget",
                "YTD_Variance",
                "CC_Name",
                "Service Name",
                "Activity_Name",
                "Resource_Name",
                "Project_Name",
                "Job_Name",
                "Code identifier",
                "ResNmNo",
                "ActNmNo",
                "ProjNmNo",
                "Region/Branch",
                "Division",
                "Resource Category",
                "Wildfire",
                "Exp_Rev",
                "Fire Activities",
                "MPRA Category",
            ],
            fields=[
                "fy",
                "download_period_str",
                "cost_centre",
                "account",
                "service",
                "activity",
                "resource",
                "project",
                "job",
                "short_code",
                "short_code_name",
                "gl_code",
                "ptd_actual",
                "ptd_budget",
                "ytd_actual",
                "ytd_budget",
                "fybudget",
                "ytd_variance",
                "cc_name",
                "service_name",
                "activity_name",
                "resource_name",
                "project_name",
                "job_name",
                "code_id",
                "res_name_no",
                "act_name_no",
                "proj_name_no",
                "region_branch",
                "division",
                "resource_category",
                "wildfire",
                "expense_revenue",
                "fire_activities",
                "mpra_category",
            ],
        )
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def ibmdata_link(self, obj):
        if obj.ibmdata:
            url = reverse("admin:ibms_ibmdata_change", args=[obj.ibmdata.pk])
            return format_html(format_string=f"<a href='{url}'>{obj.ibmdata.ibm_identifier}</a>")
        else:
            return ""

    ibmdata_link.short_description = "IBM data"

    def department_program_link(self, obj):
        if obj.department_program:
            url = reverse("admin:ibms_departmentprogram_change", args=[obj.department_program.pk])
            return format_html(format_string=f"<a href='{url}'>{obj.department_program.dept_program1}</a>")
        else:
            return ""

    department_program_link.short_description = "department program"

    def account_display(self, obj):
        return obj.get_account_display()

    account_display.short_description = "account"


@register(CorporateStrategy)
class CorporateStrategyAdmin(ModelAdmin):
    fields = ["fy", "corporate_strategy_no", "description1", "description2"]
    readonly_fields = ["fy", "corporate_strategy_no"]
    list_display = ["corporate_strategy_no", "fy", "description1"]
    list_filter = ["fy__financial_year"]
    search_fields = ["corporate_strategy_no", "description1", "description2"]
    actions = [
        export_as_csv_action(
            translations=["financial_year", "IBMSCSNo", "IBMSCSDesc1", "IBMSCSDesc2"],
            fields=["fy", "corporate_strategy_no", "description1", "description2"],
        )
    ]


@register(NCStrategicPlan)
class NCStrategicPlanAdmin(ModelAdmin):
    fields = [
        "fy",
        "strategic_plan_no",
        "direction_no",
        "direction",
        "aim_no",
        "aim1",
        "aim2",
        "action_no",
        "action",
    ]
    readonly_fields = ["fy", "strategic_plan_no"]
    list_filter = ["fy__financial_year"]
    list_display = ["fy", "strategic_plan_no", "direction_no", "direction"]
    search_fields = ["strategic_plan_no", "direction"]
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "StratPlanNo",
                "StratDirNo",
                "StratDir",
                "AimNo",
                "Aim1",
                "Aim2",
                "ActNo",
                "Action",
            ],
            fields=[
                "fy",
                "strategic_plan_no",
                "direction_no",
                "direction",
                "aim_no",
                "aim1",
                "aim2",
                "action_no",
                "action",
            ],
        )
    ]


class ServicePriorityAdmin(ModelAdmin):
    readonly_fields = ["fy"]
    list_display = [
        "service_priority_no",
        "fy",
        "category_id",
        "strategic_plan_no",
        "corporate_strategy_link",
        "strategic_plan_link",
    ]
    list_filter = ["fy__financial_year", "category_id"]
    search_fields = ["fy__financial_year", "category_id", "service_priority_no", "strategic_plan_no", "corporate_strategy_no"]

    def corporate_strategy_link(self, obj):
        if obj.corporate_strategy:
            url = reverse("admin:ibms_corporatestrategy_change", args=[obj.corporate_strategy.pk])
            return format_html(format_string=f"<a href='{url}'>{obj.corporate_strategy.corporate_strategy_no}</a>")
        else:
            return ""

    corporate_strategy_link.short_description = "corporate strategy"

    def strategic_plan_link(self, obj):
        if obj.strategic_plan:
            url = reverse("admin:ibms_ncstrategicplan_change", args=[obj.strategic_plan.pk])
            return format_html(format_string=f"<a href='{url}'>{obj.strategic_plan.strategic_plan_no}</a>")
        else:
            return ""

    strategic_plan_link.short_description = "strategic plan"


@register(GeneralServicePriority)
class GeneralServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["description2"]
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Description 1",
                "Description 2",
            ],
            fields=[
                "fy",
                "category_id",
                "service_priority_no",
                "strategic_plan_no",
                "corporate_strategy_no",
                "description",
                "description2",
            ],
        )
    ]


@register(NCServicePriority)
class NCServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + [
        "description",
        "target",
        "action",
        "milestone",
    ]
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "AssetNo",
                "Asset",
                "TargetNo",
                "Target",
                "ActionNo",
                "Action",
                "MileNo",
                "Milestone",
            ],
            fields=[
                "fy",
                "category_id",
                "service_priority_no",
                "strategic_plan_no",
                "corporate_strategy_no",
                "asset_no",
                "asset",
                "target_no",
                "target",
                "action_no",
                "action",
                "mile_no",
                "milestone",
            ],
        )
    ]


@register(PVSServicePriority)
class PVSServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["service_priority_1"]
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri",
                "PVSExampleAnnWP",
                "PVSExampleActNo",
            ],
            fields=[
                "fy",
                "category_id",
                "service_priority_no",
                "strategic_plan_no",
                "corporate_strategy_no",
                "service_priority_1",
                "description",
                "pvs_example_ann_wp",
                "pvs_example_act_no",
            ],
        )
    ]


@register(SFMServicePriority)
class SFMServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["region_branch", "description2"]
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "CategoryID",
                "Region",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri2",
            ],
            fields=[
                "fy",
                "category_id",
                "region_branch",
                "service_priority_no",
                "strategic_plan_no",
                "corporate_strategy_no",
                "description",
                "description2",
            ],
        )
    ]


@register(ERServicePriority)
class ERServicePriorityAdmin(ServicePriorityAdmin):
    search_fields = ServicePriorityAdmin.search_fields + ["classification"]
    # NOTE: The header values and the column order for this export are critical and must not be changed.
    actions = [
        export_as_csv_action(
            translations=[
                "financial_year",
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Env Regs Specific Classification",
                "Env Regs Specific Description",
            ],
            fields=[
                "fy",
                "category_id",
                "service_priority_no",
                "strategic_plan_no",
                "corporate_strategy_no",
                "classification",
                "description",
            ],
        )
    ]


# @register(Outcome)
class OutcomeAdmin(ModelAdmin):
    list_display = ["fy", "q1_input"]
    list_filter = ["fy__financial_year"]
    actions = [
        export_as_csv_action(
            translations=["financial_year", "q1_input", "q2_input", "q3_input", "q4_input"],
            fields=["fy", "q1_input", "q2_input", "q3_input", "q4_input"],
        )
    ]


@register(ServicePriorityMapping)
class ServicePriorityMappingAdmin(ModelAdmin):
    list_display = ["cost_centre_no", "fy", "wildlife_management", "parks_management", "forest_management"]
    list_filter = ["fy__financial_year", "cost_centre_no"]
    actions = [
        export_as_csv_action(
            translations=["financial_year", "cost_centre_no", "wildlife_management", "parks_management", "forest_management"],
            fields=["fy", "cost_centre_no", "wildlife_management", "parks_management", "forest_management"],
        )
    ]
