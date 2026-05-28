import codecs
import csv
import io
import os
from contextlib import contextmanager
from datetime import date, datetime
from typing import Literal

from azure.storage.blob import BlobClient
from django.conf import settings
from reversion import create_revision, set_comment

from ibms.models import (
    CorporateStrategy,
    DepartmentProgram,
    ERServicePriority,
    GeneralServicePriority,
    GLPivDownload,
    IBMData,
    NCServicePriority,
    NCStrategicPlan,
    PVSServicePriority,
    ServicePriorityMapping,
    SFMServicePriority,
)
from sfm.models import FinancialYear


class IBMSValidationError(Exception):
    """Base validation error for IBMS data import"""

    pass


class FieldLengthError(IBMSValidationError):
    """Field exceeds maximum length"""

    pass


def get_download_period():
    """Return the 'newest' download_period date value for all the GLPivDownload objects."""
    if not GLPivDownload.objects.exists():
        return date.today()
    elif not GLPivDownload.objects.filter(download_period__isnull=False).exists():
        return date.today()
    return GLPivDownload.objects.order_by("-download_period").first().download_period


def validate_char_field(field_name, max_length, data):
    """For a passed-in string value, validate it doesn't exceed a maximum length."""
    if len(data.strip()) > max_length:
        raise FieldLengthError(f"Record for field {field_name} exceeds maximum length of {max_length}: got {data}")
    return data.strip()


def validate_integer_field(field_name, data):
    """Validate field is an integer"""
    try:
        return int(str(data).strip())
    except (ValueError, TypeError):
        raise IBMSValidationError(f"Record for field {field_name} must be an integer, got: {data}")


@contextmanager
def csvload_context(file_name: str):
    """For a passed-in CSV file path, returns a reader instance having context on the underlying file
    sufficient to close the file after processing via a `with` statement.
    """
    csvfile = codecs.open(file_name, encoding="utf-8", errors="ignore")
    csv.field_size_limit(settings.CSV_FILE_LIMIT)
    try:
        reader = csv.reader(csvfile, dialect="excel")
        if not csv.Sniffer().has_header(sample=csvfile.readline()):
            reader.seek(0)
        yield reader
    finally:
        csvfile.close()


@contextmanager
def blobload_context(blob_client: BlobClient):
    """For a passed-in Azure BlobClient, streams the blob content and returns a CSV reader.
    The blob is decoded as UTF-8 (ignoring errors) and wrapped in a StringIO so it can be
    iterated without writing to disk.
    """
    csv.field_size_limit(settings.CSV_FILE_LIMIT)
    stream = blob_client.download_blob()
    content = stream.readall().decode("utf-8", errors="ignore")
    csvfile = io.StringIO(content)
    try:
        reader = csv.reader(csvfile, dialect="excel")
        if not csv.Sniffer().has_header(sample=csvfile.readline()):
            csvfile.seek(0)
        yield reader
    finally:
        csvfile.close()


def ibms_import_from_csv(
    source: str | BlobClient,
    fy: FinancialYear,
    model: type[
        GLPivDownload
        | IBMData
        | CorporateStrategy
        | NCStrategicPlan
        | DepartmentProgram
        | GeneralServicePriority
        | NCServicePriority
        | PVSServicePriority
        | SFMServicePriority
        | ERServicePriority
        | ServicePriorityMapping
    ],
) -> tuple[str, int]:
    """Generic utility function to take a CSV source (file path or Azure BlobClient),
    a FinancialYear object and an IBMS model, and import that data (update existing or create new records).
    """
    ctx = blobload_context(source) if isinstance(source, BlobClient) else csvload_context(source)
    return_str = None
    record_count = 0
    with ctx as reader:
        if model == GLPivDownload:
            for row in reader:
                record_count += 1
                # NOTE: this branch differs from the others, in that it assumes a superuser will first clear existing
                # GLPivDownload records for a given financial year.
                # We can't use bulk_create here because it doesn't set the object FK links.
                try:
                    download_period = datetime.strptime(row[0], "%d/%m/%Y")
                except ValueError:
                    raise IBMSValidationError(f"Unable to parse download_period_str value {row[0]} as a date")
                return_str = "GL Pivot Download"
                _ = GLPivDownload.objects.create(
                    fy=fy,
                    download_period=download_period,
                    download_period_str=row[0],
                    cost_centre=row[1],
                    account=row[2],
                    service=row[3],
                    activity=row[4],
                    resource=row[5],
                    project=row[6],
                    job=row[7],
                    short_code=row[8],
                    short_code_name=row[9],
                    gl_code=row[10],
                    ptd_actual=row[11],
                    ptd_budget=row[12],
                    ytd_actual=row[13],
                    ytd_budget=row[14],
                    fybudget=row[15],
                    ytd_variance=row[16],
                    cc_name=row[17],
                    service_name=row[18],
                    activity_name=row[19],
                    resource_name=row[20],
                    project_name=row[21],
                    job_name=row[22],
                    code_id=row[23],
                    res_name_no=row[24],
                    act_name_no=row[25],
                    proj_name_no=row[26],
                    region_branch=row[27],
                    division=row[28],
                    resource_category=row[29],
                    wildfire=row[30],
                    expense_revenue=row[31],
                    fire_activities=row[32],
                    mpra_category=row[33],
                )
        elif model == IBMData:
            for row in reader:
                record_count += 1
                return_str = "IBM Data"
                with create_revision():
                    if IBMData.objects.filter(fy=fy, ibm_identifier=str(row[0])).exists():
                        ibmdata = IBMData.objects.get(fy=fy, ibm_identifier=str(row[0]))
                        ibmdata.cost_centre = row[1]
                        ibmdata.account = row[2]
                        ibmdata.service = row[3]
                        ibmdata.activity = row[4]
                        ibmdata.project = row[5]
                        ibmdata.job = row[6]
                        ibmdata.budget_area = row[7]
                        ibmdata.project_sponsor = row[8]
                        ibmdata.regional_specific_info = row[9]
                        ibmdata.service_priority_id = row[10]
                        ibmdata.annual_wp_info = row[11]
                        ibmdata.priority_action_no = row[12]
                        ibmdata.priority_level = row[13]
                        ibmdata.marine_kpi = row[14]
                        ibmdata.region_project = row[15]
                        ibmdata.region_description = row[16]
                        ibmdata.save()
                        set_comment(f"{ibmdata} amended via upload")
                    else:
                        data = {
                            "fy": fy,
                            "ibm_identifier": validate_char_field("ibm_identifier", 50, row[0]),
                            "cost_centre": validate_char_field("cost_centre", 4, row[1]),
                            "account": validate_integer_field("account", row[2]),
                            "service": validate_integer_field("service", row[3]),
                            "activity": validate_char_field("activity", 4, row[4]),
                            "project": validate_char_field("project", 6, row[5]),
                            "job": validate_char_field("job", 6, row[6]),
                            "budget_area": validate_char_field("budget_area", 50, row[7]),
                            "project_sponsor": validate_char_field("project_sponsor", 50, str(row[8])),
                            "regional_specific_info": row[9],
                            "service_priority_id": validate_char_field("service_priority_id", 100, row[10]),
                            "annual_wp_info": str(row[11]),
                            "priority_action_no": str(row[12]),
                            "priority_level": str(row[13]),
                            "marine_kpi": str(row[14]),
                            "region_project": str(row[15]),
                            "region_description": str(row[16]),
                        }
                        ibmdata = IBMData(**data)
                        ibmdata.save()
                        # Repeat the save, in order to try setting the service priority on the object.
                        # We can't set this before having a PK on the object.
                        if not ibmdata.service_priority:
                            ibmdata.save()
                # Update any existing GLPivDownload objects that should now link to this object.
                for glpiv in GLPivDownload.objects.filter(fy=fy, code_id=ibmdata.ibm_identifier, ibmdata__isnull=True):
                    glpiv.save()
        elif model == CorporateStrategy:
            for row in reader:
                record_count += 1
                return_str = "IBMS Corporate Strategy"
                data = {
                    "fy": fy,
                    "corporate_strategy_no": validate_char_field("corporate_strategy_no", 10, row[0]),
                    "description1": str(row[1]),
                    "description2": str(row[2]),
                }
                query = {"fy": fy, "corporate_strategy_no": str(row[0])}
                _, _ = CorporateStrategy.objects.update_or_create(defaults=data, **query)
        elif model == NCStrategicPlan:
            for row in reader:
                record_count += 1
                return_str = "Nature Conservation"
                data = {
                    "fy": fy,
                    "strategic_plan_no": validate_char_field("strategic_plan_no", 20, row[0]),
                    "direction_no": validate_char_field("direction_no", 20, row[1]),
                    "direction": str(row[2]),
                    "aim_no": validate_char_field("direction_no", 20, row[3]),
                    "aim1": str(row[4]),
                    "aim2": str(row[5]),
                    "action_no": validate_char_field("direction_no", 20, row[6]),
                    "action": str(row[7]),
                }
                query = {"fy": fy, "strategic_plan_no": str(row[0])}
                _, _ = NCStrategicPlan.objects.update_or_create(defaults=data, **query)
        elif model == DepartmentProgram:
            for row in reader:
                record_count += 1
                data = {
                    "fy": fy,
                    "ibm_identifier": validate_char_field("ibm_identifier", 100, row[0]),
                    "dept_program1": validate_char_field("DeptProgram1", 500, row[1]),
                    "dept_program2": validate_char_field("DeptProgram2", 500, row[2]),
                    "dept_program3": validate_char_field("DeptProgram3", 500, row[3]),
                }
                query = {"fy": fy, "ibm_identifier": str(row[0])}
                department_program, _ = DepartmentProgram.objects.update_or_create(defaults=data, **query)
                # Update any GLPivDownload objects that should be linked to this object.
                for gl in GLPivDownload.objects.filter(fy=fy, code_id=department_program.ibm_identifier, department_program__isnull=True):
                    gl.save()  # Sets the FK link on save.
        elif model == GeneralServicePriority:
            for row in reader:
                record_count += 1
                data = {
                    "fy": fy,
                    "category_id": validate_char_field("category_id", 30, row[0]),
                    "service_priority_no": validate_char_field("service_priority_no", 20, row[1]),
                    "strategic_plan_no": validate_char_field("strategic_plan_no", 20, row[2]),
                    "corporate_strategy_no": row[3],
                    "description": str(row[4]),
                    "description2": str(row[5]),
                }
                query = {"fy": fy, "service_priority_no": str(row[1])}
                _, _ = GeneralServicePriority.objects.update_or_create(defaults=data, **query)
        elif model == NCServicePriority:
            for row in reader:
                record_count += 1
                return_str = "Nature Conservation Service Priority"
                data = {
                    "fy": fy,
                    "category_id": validate_char_field("category_id", 30, row[0]),
                    "service_priority_no": validate_char_field("service_priority_no", 100, row[1]),
                    "strategic_plan_no": validate_char_field("strategic_plan_no", 100, row[2]),
                    "corporate_strategy_no": validate_char_field("corporate_strategy_no", 100, row[3]),
                    "asset_no": validate_char_field("AssetNo", 5, row[4]),
                    "asset": str(row[5]),
                    "target_no": validate_char_field("Asset", 30, row[6]),
                    "target": str(row[7]),
                    "action_no": str(row[8]),
                    "action": str(row[9]),
                    "mile_no": validate_char_field("MileNo", 30, row[10]),
                    "milestone": str(row[11]),
                }
                query = {"fy": fy, "service_priority_no": str(row[1])}
                _, _ = NCServicePriority.objects.update_or_create(defaults=data, **query)
        elif model == PVSServicePriority:
            for row in reader:
                record_count += 1
                return_str = "Parks & Visitor Services Service Priority"
                data = {
                    "fy": fy,
                    "category_id": validate_char_field("category_id", 30, row[0]),
                    "service_priority_no": validate_char_field("service_priority_no", 100, row[1]),
                    "strategic_plan_no": validate_char_field("strategic_plan_no", 100, row[2]),
                    "corporate_strategy_no": row[3],
                    "service_priority_1": str(row[4]),
                    "description": str(row[5]),
                    "pvs_example_ann_wp": str(row[6]),
                    "pvs_example_act_no": str(row[7]),
                }
                query = {"fy": fy, "service_priority_no": str(row[1])}
                _, _ = PVSServicePriority.objects.update_or_create(defaults=data, **query)
        elif model == SFMServicePriority:
            for row in reader:
                record_count += 1
                return_str = "Forest Management Service Priority"
                data = {
                    "fy": fy,
                    "category_id": validate_char_field("category_id", 30, row[0]),
                    "region_branch": validate_char_field("region_branch", 20, row[1]),
                    "service_priority_no": validate_char_field("service_priority_no", 20, row[2]),
                    "strategic_plan_no": validate_char_field("strategic_plan_no", 20, row[3]),
                    "corporate_strategy_no": row[4],
                    "description": str(row[5]),
                    "description2": str(row[6]),
                }
                query = {"fy": fy, "service_priority_no": validate_char_field("service_priority_no", 20, row[2])}
                _, _ = SFMServicePriority.objects.update_or_create(defaults=data, **query)
        elif model == ERServicePriority:
            for row in reader:
                record_count += 1
                return_str = "Fire Services Service Priority"
                data = {
                    "fy": fy,
                    "category_id": validate_char_field("category_id", 30, row[0]),
                    "service_priority_no": validate_char_field("service_priority_no", 10, row[1]),
                    "strategic_plan_no": validate_char_field("strategic_plan_no", 10, row[2]),
                    "corporate_strategy_no": row[3],
                    "classification": str(row[4]),
                    "description": str(row[5]),
                }
                query = {"fy": fy, "service_priority_no": str(row[1])}
                _, _ = ERServicePriority.objects.update_or_create(defaults=data, **query)
        elif model == ServicePriorityMapping:
            for row in reader:
                record_count += 1
                return_str = "Service Priority Mapping"
                data = {
                    "fy": fy,
                    "cost_centre_no": validate_char_field("cost_centre_no", 4, row[0]),
                    "wildlife_management": validate_char_field("wildlife_management", 100, row[1]),
                    "parks_management": validate_char_field("parks_management", 100, row[2]),
                    "forest_management": validate_char_field("forest_management", 100, row[3]),
                }
                _, _ = ServicePriorityMapping.objects.update_or_create(**data)

    if not return_str:
        return model._meta.verbose_name.capitalize(), record_count
    else:
        return return_str, record_count


def validate_headers(row, valid_count, headings) -> Literal[True]:
    """For a passed-in CSV row, validate the count and content of each column.
    Raises an exception on failure, otherwise returns True."""
    column_count = len(row)
    if column_count == valid_count:  # Correct number of columns.
        # Check column headings.
        bad_headings = ""
        for k, heading in enumerate(headings):
            # If the given heading value doesn't match, append it to the error message.
            if row[k].strip().upper() != heading.upper():
                bad_headings += f"{row[k]} does not match {heading}\n"

        if bad_headings:
            raise IBMSValidationError(f"""The column headings in the CSV file do not match the required headings:\n
                            {bad_headings}""")

    else:  # Incorrect number of columns
        raise IBMSValidationError(f"""The number of columns in the CSV file do not match the required column count:\n
                        expected {valid_count}, received {column_count}""")

    return True


def validate_upload_file(in_file, file_type) -> Literal[True]:
    """Utility function called by the Upload view to validate uploaded files.
    Returns True or raises an exception.
    """
    reader = csv.reader(in_file, dialect="excel")
    row = next(reader)  # Get the first (header) row.

    if file_type == "gl_pivot_download":
        return validate_headers(
            row,
            valid_count=34,
            headings=[
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
        )
    elif file_type == "ibm_data":
        return validate_headers(
            row,
            valid_count=17,
            headings=[
                "ibmIdentifier",
                "costCentre",
                "account",
                "service",
                "activity",
                "project",
                "job",
                "budgetArea",
                "projectSponsor",
                "regionalSpecificInfo",
                "servicePriorityID",
                "annualWPInfo",
                "priorityActionNo",
                "priorityLevel",
                "marineKPI",
                "regionProject",
                "regionDescription",
            ],
        )
    elif file_type == "corp_strategy":
        return validate_headers(
            row,
            valid_count=3,
            headings=["IBMSCSNo", "IBMSCSDesc1", "IBMSCSDesc2"],
        )
    elif file_type == "nature_conservation":
        return validate_headers(
            row,
            valid_count=8,
            headings=[
                "StratPlanNo",
                "StratDirNo",
                "StratDir",
                "AimNo",
                "Aim1",
                "Aim2",
                "ActNo",
                "Action",
            ],
        )
    elif file_type == "dept_program":
        return validate_headers(
            row,
            valid_count=4,
            headings=[
                "ibmIdentifier",
                "DeptProgram1",
                "DeptProgram2",
                "DeptProgram3",
            ],
        )
    elif file_type == "er_sp":
        return validate_headers(
            row,
            valid_count=6,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Env Regs Specific Classification",
                "Env Regs Specific Description",
            ],
        )
    elif file_type == "pvs_sp":
        return validate_headers(
            row,
            valid_count=8,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri",
                "PVSExampleAnnWP",
                "PVSExampleActNo",
            ],
        )
    elif file_type == "sfm_sp":
        return validate_headers(
            row,
            valid_count=7,
            headings=[
                "CategoryID",
                "Region",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri2",
            ],
        )
    elif file_type == "general_sp":
        return validate_headers(
            row,
            valid_count=6,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Description 1",
                "Description 2",
            ],
        )
    elif file_type == "nc_sp":
        return validate_headers(
            row,
            valid_count=12,
            headings=[
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
        )
    elif file_type == "service_priority_mapping":
        return validate_headers(
            row,
            valid_count=4,
            headings=[
                "costCentreNo",
                "wildlifeManagement",
                "parksManagement",
                "forestManagement",
            ],
        )

    else:
        raise IBMSValidationError(f"Unknown file type {file_type}")


def process_upload_file(file_name, file_type, fy) -> str:
    """Utility function called by the Upload view to process an uploaded CSV file.
    Returns the type of data generated by the import."""
    if file_type == "gl_pivot_download":
        data_type = ibms_import_from_csv(file_name, fy, GLPivDownload)
    elif file_type == "ibm_data":
        data_type = ibms_import_from_csv(file_name, fy, IBMData)
    elif file_type == "corp_strategy":
        data_type = ibms_import_from_csv(file_name, fy, CorporateStrategy)
    elif file_type == "nature_conservation":
        data_type = ibms_import_from_csv(file_name, fy, NCStrategicPlan)
    elif file_type == "dept_program":
        data_type = ibms_import_from_csv(file_name, fy, DepartmentProgram)
    elif file_type == "general_sp":
        data_type = ibms_import_from_csv(file_name, fy, GeneralServicePriority)
    elif file_type == "nc_sp":
        data_type = ibms_import_from_csv(file_name, fy, NCServicePriority)
    elif file_type == "pvs_sp":
        data_type = ibms_import_from_csv(file_name, fy, PVSServicePriority)
    elif file_type == "sfm_sp":
        data_type = ibms_import_from_csv(file_name, fy, SFMServicePriority)
    elif file_type == "er_sp":
        data_type = ibms_import_from_csv(file_name, fy, ERServicePriority)
    elif file_type == "service_priority_mapping":
        data_type = ibms_import_from_csv(file_name, fy, ServicePriorityMapping)
    else:
        raise Exception(f"process_upload_file : file type {file_type} unknown")

    return data_type


def upload_file(source_path, container_name, conn_str, overwrite=True, blob_name=None, logger=None):
    """Upload a single file at `source_path` to Azure blob storage (`blob_name` destination name is optional)."""
    if not blob_name:
        blob_name = os.path.basename(source_path)

    blob_client = BlobClient.from_connection_string(conn_str, container_name, blob_name)

    if logger:
        logger.info(f"Uploading {source_path} to container {container_name}/{blob_name}")

    with open(file=source_path, mode="rb") as data:
        blob_client.upload_blob(data, overwrite=overwrite, validate_content=True)
