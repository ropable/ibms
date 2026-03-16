import codecs
import csv
from contextlib import contextmanager
from datetime import datetime
from typing import Literal

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


class IBMSValidationError(Exception):
    """Base validation error for IBMS data import"""

    pass


class FieldLengthError(IBMSValidationError):
    """Field exceeds maximum length"""

    pass


def get_download_period():
    """Return the 'newest' download_period date value for all the GLPivDownload objects."""
    if not GLPivDownload.objects.exists():
        return datetime.today()
    elif not GLPivDownload.objects.filter(download_period__isnull=False).exists():
        return datetime.today()
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
def csvload_context(file_name):
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


def import_to_ibmdata(file_name, fy):
    """Utility function to import data from the uploaded CSV to the IBMData table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "ibmIdentifier": validate_char_field("ibmIdentifier", 50, row[0]),
                "costCentre": validate_char_field("costCentre", 4, row[1]),
                "account": validate_integer_field("account", row[2]),
                "service": validate_integer_field("service", row[3]),
                "activity": validate_char_field("activity", 4, row[4]),
                "project": validate_char_field("project", 6, row[5]),
                "job": validate_char_field("job", 6, row[6]),
                "budgetArea": validate_char_field("budgetArea", 50, row[7]),
                "projectSponsor": validate_char_field("projectSponsor", 50, str(row[8])),
                "regionalSpecificInfo": row[9],
                "servicePriorityID": validate_char_field("servicePriorityID", 100, row[10]),
                "annualWPInfo": str(row[11]),
                "priorityActionNo": str(row[12]),
                "priorityLevel": str(row[13]),
                "marineKPI": str(row[14]),
                "regionProject": str(row[15]),
                "regionDescription": str(row[16]),
            }
            with create_revision():
                if IBMData.objects.filter(fy=fy, ibmIdentifier=str(row[0])).exists():
                    ibmdata = IBMData.objects.get(fy=fy, ibmIdentifier=str(row[0]))
                    ibmdata.costCentre = row[1]
                    ibmdata.account = row[2]
                    ibmdata.service = row[3]
                    ibmdata.activity = row[4]
                    ibmdata.project = row[5]
                    ibmdata.job = row[6]
                    ibmdata.budgetArea = row[7]
                    ibmdata.projectSponsor = row[8]
                    ibmdata.regionalSpecificInfo = row[9]
                    ibmdata.servicePriorityID = row[10]
                    ibmdata.annualWPInfo = row[11]
                    ibmdata.priorityActionNo = row[12]
                    ibmdata.priorityLevel = row[13]
                    ibmdata.marineKPI = row[14]
                    ibmdata.regionProject = row[15]
                    ibmdata.regionDescription = row[16]
                    ibmdata.save()
                    set_comment(f"{ibmdata} amended via upload")
                else:
                    ibmdata = IBMData(**data)
                    ibmdata.save()
                    # Repeat the save, in order to try setting the service priority on the object.
                    # We can't set this before having a PK on the object.
                    if not ibmdata.service_priority:
                        ibmdata.save()

            # Check for any existing GLPivDownload objects that should now link to this object.
            for glpiv in GLPivDownload.objects.filter(fy=fy, codeID=ibmdata.ibmIdentifier, ibmdata__isnull=True):
                glpiv.save()

        return "IBM Data"


def import_to_glpivotdownload(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the GLPivDownload table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            try:
                download_period = datetime.strptime(row[0], "%d/%m/%Y")
            except ValueError:
                download_period = None
            # NOTE: we can't use bulk_create here because it doesn't set the object FK links.
            _ = GLPivDownload.objects.create(
                fy=fy,
                download_period=download_period,
                downloadPeriod=row[0],
                costCentre=row[1],
                account=row[2],
                service=row[3],
                activity=row[4],
                resource=row[5],
                project=row[6],
                job=row[7],
                shortCode=row[8],
                shortCodeName=row[9],
                gLCode=row[10],
                ptdActual=row[11],
                ptdBudget=row[12],
                ytdActual=row[13],
                ytdBudget=row[14],
                fybudget=row[15],
                ytdVariance=row[16],
                ccName=row[17],
                serviceName=row[18],
                activityName=row[19],
                resourceName=row[20],
                projectName=row[21],
                jobName=row[22],
                codeID=row[23],
                resNameNo=row[24],
                actNameNo=row[25],
                projNameNo=row[26],
                regionBranch=row[27],
                division=row[28],
                resourceCategory=row[29],
                wildfire=row[30],
                expenseRevenue=row[31],
                fireActivities=row[32],
                mPRACategory=row[33],
            )
        return "GL Pivot Download"


def import_to_corporate_strategy(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the CorporateStrategy table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "corporateStrategyNo": validate_char_field("corporateStrategyNo", 10, row[0]),
                "description1": str(row[1]),
                "description2": str(row[2]),
            }
            query = {"fy": fy, "corporateStrategyNo": str(row[0])}
            _, _ = CorporateStrategy.objects.update_or_create(defaults=data, **query)
        return "IBMS Corporate strategy"


def import_to_nc_strategic_plan(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the NCStrategicPlan table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "strategicPlanNo": validate_char_field("strategicPlanNo", 20, row[0]),
                "directionNo": validate_char_field("directionNo", 20, row[1]),
                "direction": str(row[2]),
                "aimNo": validate_char_field("directionNo", 20, row[3]),
                "aim1": str(row[4]),
                "aim2": str(row[5]),
                "actionNo": validate_char_field("directionNo", 20, row[6]),
                "action": str(row[7]),
            }
            query = {"fy": fy, "strategicPlanNo": str(row[0])}
            _, _ = NCStrategicPlan.objects.update_or_create(defaults=data, **query)
    return "Nature Conservation"


def import_to_pvs_service_priority(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the PVSServicePriority table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "categoryID": validate_char_field("categoryID", 30, row[0]),
                "servicePriorityNo": validate_char_field("servicePriorityNo", 100, row[1]),
                "strategicPlanNo": validate_char_field("strategicPlanNo", 100, row[2]),
                "corporateStrategyNo": row[3],
                "servicePriority1": str(row[4]),
                "description": str(row[5]),
                "pvsExampleAnnWP": str(row[6]),
                "pvsExampleActNo": str(row[7]),
            }
            query = {"fy": fy, "servicePriorityNo": str(row[1])}
            _, _ = PVSServicePriority.objects.update_or_create(defaults=data, **query)
    return "Parks & Visitor Services Service priority"


def import_to_sfm_service_priority(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the SFMServicePriority table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "categoryID": validate_char_field("categoryID", 30, row[0]),
                "regionBranch": validate_char_field("regionBranch", 20, row[1]),
                "servicePriorityNo": validate_char_field("servicePriorityNo", 20, row[2]),
                "strategicPlanNo": validate_char_field("strategicPlanNo", 20, row[3]),
                "corporateStrategyNo": row[4],
                "description": str(row[5]),
                "description2": str(row[6]),
            }
            query = {"fy": fy, "servicePriorityNo": validate_char_field("servicePriorityNo", 20, row[2])}
            _, _ = SFMServicePriority.objects.update_or_create(defaults=data, **query)
    return "Forest Management Service Priority"


def import_to_er_service_priority(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the ERServicePriority table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "categoryID": validate_char_field("categoryID", 30, row[0]),
                "servicePriorityNo": validate_char_field("servicePriorityNo", 10, row[1]),
                "strategicPlanNo": validate_char_field("strategicPlanNo", 10, row[2]),
                "corporateStrategyNo": row[3],
                "classification": str(row[4]),
                "description": str(row[5]),
            }
            query = {"fy": fy, "servicePriorityNo": str(row[1])}
            _, _ = ERServicePriority.objects.update_or_create(defaults=data, **query)
    return "Fire Services Service Priority"


def import_to_general_service_priority(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the GeneralServicePriority table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "categoryID": validate_char_field("categoryID", 30, row[0]),
                "servicePriorityNo": validate_char_field("servicePriorityNo", 20, row[1]),
                "strategicPlanNo": validate_char_field("strategicPlanNo", 20, row[2]),
                "corporateStrategyNo": row[3],
                "description": str(row[4]),
                "description2": str(row[5]),
            }
            query = {"fy": fy, "servicePriorityNo": str(row[1])}

            _, _ = GeneralServicePriority.objects.update_or_create(defaults=data, **query)
    return "General Service Priority"


def import_to_nc_service_priority(file_name, fy) -> str:
    """Utility function to import data from the uploaded CSV to the NCServicePriority table."""
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "categoryID": validate_char_field("categoryID", 30, row[0]),
                "servicePriorityNo": validate_char_field("servicePriorityNo", 100, row[1]),
                "strategicPlanNo": validate_char_field("strategicPlanNo", 100, row[2]),
                "corporateStrategyNo": validate_char_field("corporateStrategyNo", 100, row[3]),
                "assetNo": validate_char_field("AssetNo", 5, row[4]),
                "asset": str(row[5]),
                "targetNo": validate_char_field("Asset", 30, row[6]),
                "target": str(row[7]),
                "actionNo": str(row[8]),
                "action": str(row[9]),
                "mileNo": validate_char_field("MileNo", 30, row[10]),
                "milestone": str(row[11]),
            }
            query = {"fy": fy, "servicePriorityNo": str(row[1])}
            _, _ = NCServicePriority.objects.update_or_create(defaults=data, **query)
    return "Nature Conservation Service Priority"


def import_to_service_priority_mappings(file_name, fy) -> str:
    """Utility function to replace data from the uploaded CSV to the ServicePriorityMapping table."""
    # First, delete any existing records.
    query_results = ServicePriorityMapping.objects.filter(fy=fy)
    if query_results.exists():
        query_results.delete()
    # Import the CSV data.
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "costCentreNo": validate_char_field("costCentreNo", 4, row[0]),
                "wildlifeManagement": validate_char_field("wildlifeManagement", 100, row[1]),
                "parksManagement": validate_char_field("parksManagement", 100, row[2]),
                "forestManagement": validate_char_field("forestManagement", 100, row[3]),
            }
            obj = ServicePriorityMapping(**data)
            obj.save()
    return "Service Priority Mapping"


def import_dept_program(file_name, fy) -> str:
    """Function to generate DepartmentProgram records from the passed-in CSV and financial year.
    Validates import data per row (safe to throw exception midway through iterator).
    """
    with csvload_context(file_name) as reader:
        for row in reader:
            data = {
                "fy": fy,
                "ibmIdentifier": validate_char_field("ibmIdentifier", 100, row[0]),
                "dept_program1": validate_char_field("DeptProgram1", 500, row[1]),
                "dept_program2": validate_char_field("DeptProgram2", 500, row[2]),
                "dept_program3": validate_char_field("DeptProgram3", 500, row[3]),
            }
            query = {"fy": fy, "ibmIdentifier": str(row[0])}
            department_program, _ = DepartmentProgram.objects.update_or_create(defaults=data, **query)

            # Filter any GLPivDownload objects that should be linked to this object
            for gl in GLPivDownload.objects.filter(fy=fy, codeID=department_program.ibmIdentifier, department_program__isnull=True):
                gl.save()  # Sets the FK link on save.
    return "Department Program"


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
            raise Exception(f"""The column headings in the CSV file do not match the required headings:\n
                            {bad_headings}""")

    else:  # Incorrect number of columns
        raise Exception(f"""The number of columns in the CSV file do not match the required column count:\n
                        expected {valid_count}, received {column_count}""")

    return True


def validate_upload_file(file, file_type) -> Literal[True]:
    """Utility function called by the Upload view to validate uploaded files.
    Returns True or raises an exception.
    """
    reader = csv.reader(file, dialect="excel")
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
                "aimNo",
                "aim1",
                "aim2",
                "actNo",
                "action",
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
                "CC No.",
                "Wildlife Management",
                "Parks Management",
                "Forest Management",
            ],
        )

    else:
        raise Exception(f"Unknown file type {file_type}")


def process_upload_file(file_name, file_type, fy) -> str:
    """Utility function called by the Upload view to process an uploaded CSV file.
    Returns the type of data generated by the import."""
    if file_type == "gl_pivot_download":
        data_type = import_to_glpivotdownload(file_name, fy)
    elif file_type == "ibm_data":
        data_type = import_to_ibmdata(file_name, fy)
    elif file_type == "corp_strategy":
        data_type = import_to_corporate_strategy(file_name, fy)
    elif file_type == "er_sp":
        data_type = import_to_er_service_priority(file_name, fy)
    elif file_type == "pvs_sp":
        data_type = import_to_pvs_service_priority(file_name, fy)
    elif file_type == "sfm_sp":
        data_type = import_to_sfm_service_priority(file_name, fy)
    elif file_type == "nature_conservation":
        data_type = import_to_nc_strategic_plan(file_name, fy)
    elif file_type == "dept_program":
        data_type = import_dept_program(file_name, fy)
    elif file_type == "general_sp":
        data_type = import_to_general_service_priority(file_name, fy)
    elif file_type == "nc_sp":
        data_type = import_to_nc_service_priority(file_name, fy)
    elif file_type == "service_priority_mapping":
        data_type = import_to_service_priority_mappings(file_name, fy)
    else:
        raise Exception(f"process_upload_file : file type {file_type} unknown")

    return data_type
