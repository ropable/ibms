from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout, Submit
from django import forms
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from ibms.models import (
    ERServicePriority,
    GeneralServicePriority,
    GLPivDownload,
    IBMData,
    NCServicePriority,
    PVSServicePriority,
    SFMServicePriority,
)
from ibms.models import FinancialYear


def get_generic_choices(model, key, allow_null=False):
    """Generates a list of choices for a drop down from a model and key."""
    choices = [("", "----------")] if allow_null else []
    for i in model.objects.all().values_list(key, flat=True).distinct():
        choices.append((str(i), str(i)))
    choices.sort()

    return choices


class HelperForm(forms.Form):
    """Base form class with a crispy_forms FormHelper."""

    def __init__(self, *args, **kwargs):
        super(HelperForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-3 col-lg-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-6 col-lg-4"


class FinancialYearFilterForm(HelperForm):
    """Base form class to be include a financial year filter select."""

    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all().order_by("-financial_year"), empty_label=None, required=True
    )


class ClearGLPivotForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(ClearGLPivotForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-md-10 col-lg-9 alert alert-warning">
                Please confirm that you want to clear all GL Pivot entries for the selected financial year.</div></div>"""),
            Div(
                "financial_year",
                Submit("confirm", "Confirm", css_class="btn-danger"),
                Submit("cancel", "Cancel"),
                css_class="col-sm-offset-3 col-md-offset-2 col-lg-offset-1",
            ),
        )


class UploadForm(FinancialYearFilterForm):
    upload_file_type = forms.ChoiceField(
        choices=(
            (None, "----------"),
            ("General", (("gl_pivot_download", "GL Pivot Download"), ("ibm_data", "IBM Data"))),
            (
                "Strategic",
                (
                    ("corp_strategy", "IBMS Corporate Strategy"),
                    ("nature_conservation", "Nature Conservation"),
                    ("dept_program", "Department Program"),
                ),
            ),
            (
                "Service Priorities",
                (
                    ("general_sp", "General"),
                    ("nc_sp", "Nature Conservation"),
                    ("pvs_sp", "Parks & Visitor Services"),
                    ("er_sp", "Fire Services"),
                    ("sfm_sp", "Forest Management"),
                    ("service_priority_mapping", "Service Priority Mapping"),
                ),
            ),
        )
    )
    upload_file = forms.FileField(label="CSV file")

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        # crispy_forms layout
        self.helper.layout = Layout(
            "upload_file_type",
            "upload_file",
            "financial_year",
            Div(Submit("upload", "Upload"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    def clean(self):
        # Validation: CSV files only.
        upload = self.cleaned_data.get("upload_file")
        if upload and upload.content_type not in ["text/plain", "text/csv", "application/vnd.ms-excel"]:
            self._errors["upload_file"] = self.error_class(["File type is not allowed (.csv only)"])
        if upload and upload.size > settings.MAX_UPLOAD_SIZE:
            self._errors["upload_file"] = self.error_class([f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE} bytes"])
        return self.cleaned_data


class DownloadForm(FinancialYearFilterForm):
    def __init__(self, request, *args, **kwargs):
        super(DownloadForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "cost_centre", allow_null=True), required=False
        )
        self.fields["region"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "region_branch", allow_null=True),
            required=False,
            label="Region/branch",
        )
        self.fields["division"] = forms.ChoiceField(choices=get_generic_choices(GLPivDownload, "division", allow_null=True), required=False)

        # Disable several fields on initial form load.
        for field in ["cost_centre", "region", "division"]:
            self.fields[field].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            "financial_year",
            "cost_centre",
            "region",
            "division",
            Div(Submit("download", "Download"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    def clean(self):
        """Validate that at least one (but only one) of CC, region or division
        has been selected.
        Superusers may choose none of these.
        """
        if not self.request.user.is_superuser:
            d = self.cleaned_data
            if not d["cost_centre"] and not d["region"] and not d["division"]:
                valid = False
            elif d["cost_centre"] and d["region"] and d["division"]:
                valid = False
            elif d["cost_centre"] and (d["region"] or d["division"]):
                valid = False
            elif d["region"] and (d["cost_centre"] or d["division"]):
                valid = False
            elif d["division"] and (d["cost_centre"] or d["region"]):
                valid = False
            else:
                valid = True
            if not valid:
                msg = "You must choose either Cost Centre OR Region/Branch OR Division"
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
                self._errors["division"] = self.error_class([msg])
        return self.cleaned_data


class DataAmendmentForm(FinancialYearFilterForm):
    def __init__(self, request, *args, **kwargs):
        super(DataAmendmentForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "cost_centre", allow_null=True), required=False
        )
        self.fields["region"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "region_branch", allow_null=True),
            required=False,
            label="Region/branch",
        )
        self.fields["service"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "service", allow_null=True), required=False, label="Service"
        )
        self.fields["budget_area"] = forms.ChoiceField(
            choices=get_generic_choices(IBMData, "budget_area", allow_null=True), required=False, label="Budget Area"
        )
        self.fields["project_sponsor"] = forms.ChoiceField(
            choices=get_generic_choices(IBMData, "project_sponsor", allow_null=True),
            required=False,
            label="Project Sponsor",
        )
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "category_id"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "category_id"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "category_id"),
            required=False,
            label="Forest Management",
        )

        # Disable several fields on initial form load.
        if not self.request.user.is_superuser:
            for field in ["cost_centre", "region", "service", "budget_area", "project_sponsor"]:
                self.fields[field].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:
                </div></div>"""),
            "financial_year",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select either Cost Centre OR Region/Branch:</div>
                </div>"""),
            "cost_centre",
            "region",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select appropriate filter(s) to generate the codes required (optional):
                </div></div>"""),
            "service",
            "budget_area",
            "project_sponsor",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relevant Service Priorities for your Region/Branch:
                </div></div>"""),
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("dataamendment", "Data Amendment"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    def clean(self):
        # Non-superusers must choose either cost centre or region/branch.
        # Superusers may choose neither.
        if not self.request.user.is_superuser:
            if not self.cleaned_data["cost_centre"] and not self.cleaned_data["region"]:
                msg = "You must choose either Cost Centre OR Region/Branch"
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
            if self.cleaned_data["cost_centre"] and self.cleaned_data["region"]:
                msg = "You must choose either Cost Centre OR Region/Branch"
                self._errors["cost_centre"] = self.error_class([msg])
                self._errors["region"] = self.error_class([msg])
        return self.cleaned_data


class CodeUpdateForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(CodeUpdateForm, self).__init__(*args, **kwargs)
        self.fields["cost_centre"] = forms.ChoiceField(
            choices=get_generic_choices(GLPivDownload, "cost_centre", allow_null=True), required=True
        )
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "category_id"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "category_id"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "category_id"),
            required=False,
            label="Forest Management",
        )

        # Initially disable the cost centre field on form load.
        self.fields["cost_centre"].widget.attrs.update({"disabled": ""})

        # crispy_forms layout
        self.helper.layout = Layout(
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select a financial year:
                </div></div>"""),
            "financial_year",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Please select a Cost Centre
                </div></div>"""),
            "cost_centre",
            HTML("""<div class="row">
                <div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                You must select relevant Service Priorities for your cost centre
                </div></div>"""),
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("codeupdate", "Code Update"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class ManagerCodeUpdateForm(FinancialYearFilterForm):
    def __init__(self, *args, **kwargs):
        super(ManagerCodeUpdateForm, self).__init__(*args, **kwargs)
        self.fields["report_type"] = forms.ChoiceField(
            choices=(
                (None, "----------"),
                ("dj0", "DJ0 activities only"),
                ("no-dj0", "Exclude DJ0 activities"),
            ),
            label="Report type",
            required=True,
        )
        self.fields["ncChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(NCServicePriority, "category_id"),
            required=False,
            label="Wildlife Management",
        )
        self.fields["pvsChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(PVSServicePriority, "category_id"),
            required=False,
            label="Parks Management",
        )
        self.fields["fmChoice"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=get_generic_choices(SFMServicePriority, "category_id"),
            required=False,
            label="Forest Management",
        )

        self.helper.layout = Layout(
            "report_type",
            "financial_year",
            HTML('<div class="checkbox">'),
            "ncChoice",
            "pvsChoice",
            "fmChoice",
            HTML("</div>"),
            Div(Submit("codeupdate", "Code Update"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class IbmDataFilterForm(forms.Form):
    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all().order_by("-financial_year"), empty_label=None, required=True
    )
    cost_centre = forms.ChoiceField(choices=[("", "--------")], required=False)
    region = forms.ChoiceField(choices=[("", "--------")], required=False, label="Region/branch")
    budget_area = forms.ChoiceField(choices=[("", "--------")], required=False)
    project_sponsor = forms.ChoiceField(choices=[("", "--------")], required=False)
    service = forms.ChoiceField(choices=[("", "--------")], required=False)
    project = forms.ChoiceField(choices=[("", "--------")], required=False)
    job = forms.ChoiceField(choices=[("", "--------")], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set field options for CC and Region/branch.
        fy = FinancialYear.objects.get(financial_year=kwargs["initial"]["financial_year"])
        cost_centres = IBMData.objects.filter(fy=fy, cost_centre__isnull=False).values_list("cost_centre", flat=True).distinct()
        self.fields["cost_centre"].choices += sorted([(i, i) for i in cost_centres])
        regions = GLPivDownload.objects.filter(fy=fy, region_branch__isnull=False).values_list("region_branch", flat=True).distinct()
        self.fields["region"].choices += sorted([(i, i) for i in regions])

        if "cost_centre" in kwargs["initial"] and kwargs["initial"]["cost_centre"]:
            budget_areas = (
                IBMData.objects.filter(fy=fy, cost_centre=kwargs["initial"]["cost_centre"], budget_area__isnull=False)
                .values_list("budget_area", flat=True)
                .distinct()
            )
            self.fields["budget_area"].choices += sorted([(i, i) for i in budget_areas if i])
            project_sponsors = (
                IBMData.objects.filter(fy=fy, cost_centre=kwargs["initial"]["cost_centre"], project_sponsor__isnull=False)
                .values_list("project_sponsor", flat=True)
                .distinct()
            )
            self.fields["project_sponsor"].choices += sorted([(i, i) for i in project_sponsors if i])
            services = (
                IBMData.objects.filter(fy=fy, cost_centre=kwargs["initial"]["cost_centre"], service__isnull=False)
                .values_list("service", flat=True)
                .distinct()
            )
            self.fields["service"].choices += sorted([(i, i) for i in services if i])
            projects = (
                IBMData.objects.filter(fy=fy, cost_centre=kwargs["initial"]["cost_centre"], project__isnull=False)
                .values_list("project", flat=True)
                .distinct()
            )
            self.fields["project"].choices += sorted([(i, i) for i in projects if i])
            jobs = (
                IBMData.objects.filter(fy=fy, cost_centre=kwargs["initial"]["cost_centre"], job__isnull=False)
                .values_list("job", flat=True)
                .distinct()
            )
            self.fields["job"].choices += sorted([(i, i) for i in jobs if i])

        if "region" in kwargs["initial"] and kwargs["initial"]["region"]:
            region_branch = kwargs["initial"]["region"]
            cost_centres = set(GLPivDownload.objects.filter(fy=fy, region_branch=region_branch).values_list("cost_centre", flat=True))

            budget_areas = (
                IBMData.objects.filter(fy=fy, cost_centre__in=cost_centres, budget_area__isnull=False)
                .values_list("budget_area", flat=True)
                .distinct()
            )
            self.fields["budget_area"].choices += sorted([(i, i) for i in budget_areas if i])
            project_sponsors = (
                IBMData.objects.filter(fy=fy, cost_centre__in=cost_centres, project_sponsor__isnull=False)
                .values_list("project_sponsor", flat=True)
                .distinct()
            )
            self.fields["project_sponsor"].choices += sorted([(i, i) for i in project_sponsors if i])
            services = (
                IBMData.objects.filter(fy=fy, cost_centre__in=cost_centres, service__isnull=False)
                .values_list("service", flat=True)
                .distinct()
            )
            self.fields["service"].choices += sorted([(i, i) for i in services if i])
            projects = (
                IBMData.objects.filter(fy=fy, cost_centre__in=cost_centres, project__isnull=False)
                .values_list("project", flat=True)
                .distinct()
            )
            self.fields["project"].choices += sorted([(i, i) for i in projects if i])
            jobs = IBMData.objects.filter(fy=fy, cost_centre__in=cost_centres, job__isnull=False).values_list("job", flat=True).distinct()
            self.fields["job"].choices += sorted([(i, i) for i in jobs if i])

        # crispy_forms layout
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-3 col-lg-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-6 col-lg-4"
        self.helper.layout = Layout(
            "financial_year",
            HTML("""<div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Select either Cost Centre OR Region/Branch:</div>"""),
            "cost_centre",
            "region",
            HTML("""<div class="col-sm-12 col-md-9 col-lg-6 alert alert-info">
                Select additional filter(s) to limit records returned:
                </div>"""),
            "budget_area",
            "project_sponsor",
            "service",
            "project",
            "job",
            Div(Submit("filter", "Filter"), css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )


class ListTextWidget(forms.TextInput):
    """A customised TextInput widget, which accepts a list of options and renders
    a datalist element inline with the text input element.
    References:
      - https://docs.djangoproject.com/en/dev/ref/forms/widgets/#customizing-widget-instances
      - https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data_list
    """

    def __init__(self, name, data_list, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({"list": f"{self._name}_list"})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = f'<datalist id="{self._name}_list">'
        for item in self._list:
            data_list += f'<option value="{item}">'
        data_list += "</datalist>"

        return text_html + data_list


class IbmDataForm(forms.ModelForm):
    """Edit form in use for the Data Amendment view."""

    budget_area = forms.CharField(
        label="Budget area",
        required=True,
        help_text="Free text. Delete existing value and click to display list.",
    )
    project_sponsor = forms.CharField(
        label="Project sponsor",
        required=False,
        help_text="Free text. Delete existing value and click to display list.",
    )
    service_priority_id = forms.ChoiceField(
        choices=[("", "--------")],
        label="Service priority ID",
        required=False,
    )
    marine_kpi = forms.CharField(
        label="Marine KPI",
        required=False,
        help_text="Mandatory for Marine Parks. Free text. Delete existing value and click to display list.",
    )
    region_project = forms.CharField(
        label="Region project",
        required=False,
        help_text="Mandatory for PfoP. Free text. Delete existing value and click to display list.",
    )
    region_description = forms.CharField(
        label="Region description",
        required=False,
        help_text="Mandatory for PfoP. Free text. Delete existing value and click to display list.",
    )

    save_button = Submit("save", "Save", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]

        # CharFields using ListTextWidget
        budget_areas = (
            IBMData.objects.filter(fy=instance.fy, cost_centre=instance.cost_centre, budget_area__isnull=False)
            .exclude(budget_area="")
            .values_list("budget_area", flat=True)
            .distinct()
        )
        budget_areas = sorted(list(budget_areas))
        self.fields["budget_area"].widget = ListTextWidget(name="budget_areas", data_list=budget_areas)

        project_sponsors = (
            IBMData.objects.filter(fy=instance.fy, cost_centre=instance.cost_centre, project_sponsor__isnull=False)
            .exclude(project_sponsor="")
            .values_list("project_sponsor", flat=True)
            .distinct()
        )
        project_sponsors = sorted(list(project_sponsors))
        self.fields["project_sponsor"].widget = ListTextWidget(name="project_sponsors", data_list=project_sponsors)

        # Service priority ID value options are sourced from a different model, depending on the instances service value.
        if instance.service == 12:
            service_priority_ids = (
                GeneralServicePriority.objects.filter(fy=instance.fy).values_list("service_priority_no", flat=True).distinct()
            )
        elif instance.service == 24:
            service_priority_ids = NCServicePriority.objects.filter(fy=instance.fy).values_list("service_priority_no", flat=True).distinct()
        elif instance.service == 32:
            service_priority_ids = PVSServicePriority.objects.filter(fy=instance.fy).values_list("service_priority_no", flat=True).distinct()
        elif instance.service in [41, 42, 43]:
            service_priority_ids = SFMServicePriority.objects.filter(fy=instance.fy).values_list("service_priority_no", flat=True).distinct()
        elif instance.service in [72, 75]:
            service_priority_ids = ERServicePriority.objects.filter(fy=instance.fy).values_list("service_priority_no", flat=True).distinct()
        else:
            service_priority_ids = (
                IBMData.objects.filter(fy=instance.fy, cost_centre=instance.cost_centre, service_priority_id__isnull=False)
                .values_list("service_priority_id", flat=True)
                .distinct()
            )
        self.fields["service_priority_id"].choices += sorted([(i, i) for i in service_priority_ids if i])

        marine_kpis = (
            IBMData.objects.filter(fy=instance.fy, cost_centre=instance.cost_centre, marine_kpi__isnull=False)
            .exclude(marine_kpi="")
            .values_list("marine_kpi", flat=True)
            .distinct()
        )
        marine_kpis = sorted(list(marine_kpis))
        self.fields["marine_kpi"].widget = ListTextWidget(name="marine_kpi", data_list=marine_kpis)

        region_projects = (
            IBMData.objects.filter(fy=instance.fy, cost_centre=instance.cost_centre, region_project__isnull=False)
            .exclude(region_project="")
            .values_list("region_project", flat=True)
            .distinct()
        )
        region_projects = sorted(list(region_projects))
        self.fields["region_project"].widget = ListTextWidget(name="region_project", data_list=region_projects)

        region_descriptions = (
            IBMData.objects.filter(fy=instance.fy, cost_centre=instance.cost_centre, region_description__isnull=False)
            .exclude(region_description="")
            .values_list("region_description", flat=True)
            .distinct()
        )
        region_descriptions = sorted(list(region_descriptions))
        self.fields["region_description"].widget = ListTextWidget(name="region_description", data_list=region_descriptions)

        self.fields["annual_wp_info"].widget = forms.Textarea(attrs={"cols": "40", "rows": "4"})

        # Readonly fields
        for field in [
            "ibm_identifier",
            "fy",
            "cost_centre",
            "account",
            "service",
            "activity",
            "project",
            "job",
        ]:
            self.fields[field].required = False
            self.fields[field].disabled = True
            self.fields[field].widget = forms.TextInput(attrs={"readonly": "readonly"})

        # Business rule: for accounts 1, 2 and 42, the service_priority_id field is compulsory.
        if instance.account in [1, 2, 42]:
            self.fields["service_priority_id"].required = True

        # Non-essential Textarea fields.
        for field in [
            "regional_specific_info",
            "annual_wp_info",
            "priority_action_no",
            "priority_level",
        ]:
            self.fields[field].required = False
            self.fields[field].help_text = "Free text."

        # Use smaller textarea widgets.
        for field in [
            "regional_specific_info",
            "priority_action_no",
            "priority_level",
        ]:
            self.fields[field].widget = forms.Textarea(attrs={"cols": "40", "rows": "1"})

        # crispy_forms layout
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-10"
        self.helper.help_text_inline = True
        self.helper.attrs = {"novalidate": ""}
        self.helper.layout = Layout(
            "ibm_identifier",
            "fy",
            "budget_area",
            "project_sponsor",
            "regional_specific_info",
            "service_priority_id",
            "annual_wp_info",
            "cost_centre",
            "account",
            "service",
            "activity",
            "project",
            "job",
            "priority_action_no",
            "priority_level",
            "marine_kpi",
            "region_project",
            "region_description",
            Div(self.save_button, self.cancel_button, css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    class Meta:
        model = IBMData
        fields = [
            "ibm_identifier",
            "fy",
            "budget_area",
            "project_sponsor",
            "regional_specific_info",
            "service_priority_id",
            "annual_wp_info",
            "cost_centre",
            "account",
            "service",
            "activity",
            "project",
            "job",
            "priority_action_no",
            "priority_level",
            "marine_kpi",
            "region_project",
            "region_description",
        ]
        exclude = ["id"]


class CodeUpdateCreateForm(forms.ModelForm):
    """Create form used for the Code Update view."""

    fy = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
        required=True,
        disabled=True,
        label="Financial year",
    )
    cost_centre = forms.ChoiceField(choices=[("", "--------")], required=True, label="Cost centre")
    service = forms.ChoiceField(
        choices=[
            ("", "--------"),
            ("12", "12"),
            ("24", "24"),
            ("32", "32"),
            ("41", "41"),
            ("42", "42"),
            ("43", "43"),
            ("72", "72"),
            ("75", "75"),
        ],
        required=True,
    )
    save_button = Submit("save", "Save", css_class="btn-lg")
    cancel_button = Submit("cancel", "Cancel", css_class="btn-secondary")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Take the existing model form fields and apply the required restrictions and validation rules.
        fy = FinancialYear.objects.get(financial_year=kwargs["initial"]["financial_year"])
        cost_centres = GLPivDownload.objects.filter(fy=fy, cost_centre__isnull=False).values_list("cost_centre", flat=True).distinct()
        budget_areas = (
            IBMData.objects.filter(fy=fy, budget_area__isnull=False).exclude(budget_area="").values_list("budget_area", flat=True).distinct()
        )
        budget_areas = sorted(list(budget_areas))

        self.fields["fy"].queryset = FinancialYear.objects.filter(financial_year=kwargs["initial"]["financial_year"])
        self.fields["fy"].initial = fy
        self.fields["cost_centre"].choices += sorted([(i, i) for i in cost_centres])
        self.fields["account"].required = True
        self.fields["account"].validators = [
            MaxValueValidator(limit_value=99, message="Account value maximum is 99."),
            MinValueValidator(limit_value=1, message="Account value minimum is 01."),
        ]
        self.fields["account"].widget.attrs.update({"min": 1, "max": 99})
        self.fields["account"].help_text = "Numeric integer, minimum 1, maximum 99."
        self.fields["activity"].required = True
        self.fields["activity"].help_text = "Two letters followed by one number or letter."
        self.fields["activity"].validators = [
            RegexValidator(
                regex=r"^[A-Za-z]{2}[A-Za-z0-9]$", message="Activity value must be two letters followed by one number or letter."
            )
        ]
        self.fields["activity"].widget.attrs.update({"placeholder": "---"})
        self.fields["activity"].widget.attrs.update({"maxlength": "3"})
        self.fields["activity"].widget.attrs.update({"pattern": "[A-Za-z]{2}[A-Za-z0-9]"})
        self.fields["project"].required = True
        self.fields["project"].help_text = "Four characters, alphanumeric."
        self.fields["project"].validators = [
            RegexValidator(regex=r"^[A-Za-z0-9]{4}$", message="Project value must be four alphanumeric characters.")
        ]
        self.fields["project"].widget.attrs.update({"placeholder": "----"})
        self.fields["project"].widget.attrs.update({"maxlength": "4"})
        self.fields["project"].widget.attrs.update({"pattern": "[A-Za-z0-9]{4}"})
        self.fields["job"].required = True
        self.fields["job"].help_text = "Three characters, alphanumeric."
        self.fields["job"].validators = [
            RegexValidator(regex=r"^[A-Za-z0-9]{3}$", message="Job value must be three alphanumeric characters.")
        ]
        self.fields["job"].widget.attrs.update({"placeholder": "---"})
        self.fields["job"].widget.attrs.update({"maxlength": "3"})
        self.fields["job"].widget.attrs.update({"pattern": "[A-za-z0-9]{3}"})

        # CharFields using ListTextWidget
        self.fields["budget_area"].widget = ListTextWidget(name="budget_areas", data_list=budget_areas)
        self.fields["budget_area"].help_text = "Free text. Click to display list of existing values."

        # crispy_forms layout
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-xs-12 col-sm-4 col-md-2"
        self.helper.field_class = "col-xs-12 col-sm-8 col-md-10"
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            "fy",
            "cost_centre",
            "account",
            "service",
            "activity",
            "project",
            "job",
            "budget_area",
            Div(self.save_button, self.cancel_button, css_class="col-sm-offset-4 col-md-offset-3 col-lg-offset-2"),
        )

    class Meta:
        model = IBMData
        fields = [
            "fy",
            "cost_centre",
            "account",
            "service",
            "activity",
            "project",
            "job",
            "budget_area",
        ]
        exclude = ["id"]

    def clean(self):
        # Business rule: users may not input activity DJ0.
        if "activity" in self.cleaned_data and self.cleaned_data["activity"].lower() == "dj0":
            self._errors["activity"] = self.error_class(
                ["IBMS information for activity DJ0 (Bushfire) is system generated, not available for user input."]
            )

        return self.cleaned_data
