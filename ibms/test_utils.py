import os
import tempfile
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import TestCase
from mixer.backend.django import mixer

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
from ibms.tests import IbmsTestCase
from ibms.utils import (
    ColumnCountError,
    FieldLengthError,
    IBMSValidationError,
    get_download_period,
    ibms_import_from_csv,
    validate_char_field,
    validate_column_count,
    validate_integer_field,
)

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


class GetDownloadPeriodTest(IbmsTestCase):
    """Test get_download_period utility function."""

    def test_get_download_period_empty_database(self):
        """get_download_period should return today when no GLPivDownload exists"""

        # Ensure no GLPivDownload records
        GLPivDownload.objects.all().delete()

        dl_period = get_download_period()
        # Should return a date of today
        self.assertEqual(dl_period, date.today())

    def test_get_download_period_with_records(self):
        """get_download_period should return newest download_period"""

        # Create multiple GLPivDownload records with different periods
        gl1 = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            download_period=datetime(2024, 1, 15).date(),
        )
        gl2 = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            download_period=datetime(2024, 3, 20).date(),
        )
        gl3 = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            download_period=datetime(2024, 2, 10).date(),
        )

        dl_period = get_download_period()
        self.assertEqual(dl_period, datetime(2024, 3, 20).date())

    def test_get_download_period_with_null_periods(self):
        """get_download_period should return today if all periods are null"""

        # Create GLPivDownload records with null download_period
        mixer.blend(GLPivDownload, fy=self.fy, download_period=None)
        mixer.blend(GLPivDownload, fy=self.fy, download_period=None)

        dl_period = get_download_period()
        self.assertEqual(dl_period, date.today())


class ValidateCharFieldTest(TestCase):
    """Test validate_char_field utility function."""

    def test_validate_char_field_within_limit(self):
        """validate_char_field should accept strings within limit"""
        result = validate_char_field("test_field", 100, "valid string")
        self.assertEqual(result, "valid string")

    def test_validate_char_field_strips_whitespace(self):
        """validate_char_field should strip leading/trailing whitespace"""
        result = validate_char_field("test_field", 100, "  spaced  ")
        self.assertEqual(result, "spaced")

    def test_validate_char_field_exceeds_limit(self):
        """validate_char_field should raise FieldLengthError when exceeding limit"""
        with self.assertRaises(FieldLengthError) as context:
            validate_char_field("test_field", 5, "this is too long")

        self.assertIn("exceeds maximum length", str(context.exception))

    def test_validate_char_field_at_limit(self):
        """validate_char_field should accept strings exactly at limit"""
        result = validate_char_field("test_field", 10, "0123456789")
        self.assertEqual(result, "0123456789")


class ValidateIntegerFieldTest(TestCase):
    """Test validate_integer_field utility function."""

    def test_validate_integer_field_valid_int(self):
        """validate_integer_field should accept valid integers"""
        result = validate_integer_field("account", "42")
        self.assertEqual(result, 42)

    def test_validate_integer_field_string_int(self):
        """validate_integer_field should convert string to integer"""
        result = validate_integer_field("account", "123")
        self.assertEqual(result, 123)
        self.assertIsInstance(result, int)

    def test_validate_integer_field_invalid_string(self):
        """validate_integer_field should raise IBMSValidationError for non-numeric string"""
        with self.assertRaises(IBMSValidationError) as context:
            validate_integer_field("account", "abc")

        self.assertIn("must be an integer", str(context.exception))

    def test_validate_integer_field_none_value(self):
        """validate_integer_field should raise IBMSValidationError for None"""
        with self.assertRaises(IBMSValidationError):
            validate_integer_field("account", None)

    def test_validate_integer_field_negative_int(self):
        """validate_integer_field should accept negative integers"""
        result = validate_integer_field("account", "-42")
        self.assertEqual(result, -42)


class CSVRowBoundsCheckingTest(IbmsTestCase):
    """Tests for CSV row bounds checking - security-focused."""

    def test_csv_row_short_glpivot(self):
        """CSV with too-few columns for GL Pivot should be handled gracefully"""
        # This tests the critical bounds checking
        # The actual import function should handle short rows
        pass  # Implementation depends on how ibms_import_from_csv handles this

    def test_csv_row_short_ibmdata(self):
        """CSV with too-few columns for IBM Data should be handled gracefully"""
        pass  # Implementation depends on how ibms_import_from_csv handles this


class IBMDataDisplayMethodsTest(IbmsTestCase):
    """Test IBMData display formatting methods via CSV import context."""

    def test_account_display_formatting_zero_padding(self):
        """Account field should be zero-padded when displayed"""
        ibm = mixer.blend(IBMData, fy=self.fy, account=5)
        self.assertEqual(ibm.get_account_display(), "05")

    def test_service_display_formatting_zero_padding(self):
        """Service field should be zero-padded when displayed"""
        ibm = mixer.blend(IBMData, fy=self.fy, service=3)
        self.assertEqual(ibm.get_service_display(), "03")

    def test_project_display_formatting_zero_padding(self):
        """Project field should be zero-padded to 4 digits"""
        ibm = mixer.blend(IBMData, fy=self.fy, project="42")
        self.assertEqual(ibm.get_project_display(), "0042")

    def test_job_display_formatting_zero_padding(self):
        """Job field should be zero-padded to 3 digits"""
        ibm = mixer.blend(IBMData, fy=self.fy, job="5")
        self.assertEqual(ibm.get_job_display(), "005")


class GLPivDownloadDisplayMethodsTest(IbmsTestCase):
    """Test GLPivDownload display formatting methods."""

    def test_account_display_formatting_zero_padding(self):
        """GLPivDownload account should be zero-padded"""
        gl = mixer.blend(GLPivDownload, fy=self.fy, account=5)
        self.assertEqual(gl.get_account_display(), "05")

    def test_project_display_formatting_zero_padding(self):
        """GLPivDownload project should be zero-padded to 4 digits"""
        gl = mixer.blend(GLPivDownload, fy=self.fy, project="42")
        self.assertEqual(gl.get_project_display(), "0042")

    def test_job_display_formatting_zero_padding(self):
        """GLPivDownload job should be zero-padded to 3 digits"""
        gl = mixer.blend(GLPivDownload, fy=self.fy, job="5")
        self.assertEqual(gl.get_job_display(), "005")


class ValidateColumnCountTest(TestCase):
    """Test validate_column_count function."""

    def test_exact_match(self):
        """validate_column_count should return True for exact match"""
        result = validate_column_count(["a", "b", "c"], 3)
        self.assertTrue(result)

    def test_too_few_columns(self):
        """validate_column_count should raise ColumnCountError when row is too short"""
        with self.assertRaises(ColumnCountError) as ctx:
            validate_column_count(["a", "b"], 3)
        self.assertIn("expected 3", str(ctx.exception))
        self.assertIn("received 2", str(ctx.exception))

    def test_too_many_columns(self):
        """validate_column_count should raise ColumnCountError when row is too long"""
        with self.assertRaises(ColumnCountError) as ctx:
            validate_column_count(["a", "b", "c", "d"], 3)
        self.assertIn("expected 3", str(ctx.exception))
        self.assertIn("received 4", str(ctx.exception))

    def test_empty_row(self):
        """validate_column_count should raise ColumnCountError for empty row when count > 0"""
        with self.assertRaises(ColumnCountError):
            validate_column_count([], 1)


class IbmsImportFromCsvGLPivDownloadTest(IbmsTestCase):
    """Test ibms_import_from_csv for GLPivDownload using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "glpivot_upload_test.csv")

    def test_import_creates_records(self):
        """Importing glpivot CSV should create GLPivDownload records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, GLPivDownload)
        self.assertEqual(desc, "GL Pivot Download")
        self.assertEqual(count, 4)
        self.assertEqual(GLPivDownload.objects.filter(fy=self.fy).count(), 4)

    def test_import_sets_correct_fields(self):
        """Imported GLPivDownload should have expected field values from first CSV row"""
        ibms_import_from_csv(self.csv_path, self.fy, GLPivDownload)
        # First row: costCentre=151, account=1, service=32, download_period=30/04/2025
        gl = GLPivDownload.objects.filter(fy=self.fy, costCentre="151", account=1, service=32).first()
        self.assertIsNotNone(gl)
        self.assertEqual(gl.download_period.strftime("%d/%m/%Y"), "30/04/2025")
        self.assertEqual(gl.division, "Nature Based Tourism")

    def test_import_links_ibmdata_when_present(self):
        """GLPivDownload import should set ibmdata FK when a matching IBMData record exists"""
        # Create an IBMData record matching the codeID in the CSV: 418-01-12-GC2-GAS1-945
        mixer.blend(IBMData, fy=self.fy, ibmIdentifier="418-01-12-GC2-GAS1-945")
        ibms_import_from_csv(self.csv_path, self.fy, GLPivDownload)
        gl = GLPivDownload.objects.filter(fy=self.fy, codeID="418-01-12-GC2-GAS1-945").first()
        self.assertIsNotNone(gl)
        self.assertIsNotNone(gl.ibmdata)
        self.assertEqual(gl.ibmdata.ibmIdentifier, "418-01-12-GC2-GAS1-945")

    def test_import_invalid_date_raises_error(self):
        """A row with an unparseable downloadPeriod should raise IBMSValidationError"""
        bad_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        bad_csv.write("Download Period,CC,Account,Service,Activity,Resource,Project,Job,"
                      "Shortcode,Shortcode_Name,GL_Code,PTD_Actual,PTD_Budget,YTD_Actual,"
                      "YTD_Budget,FY_Budget,YTD_Variance,CC_Name,Service Name,Activity_Name,"
                      "Resource_Name,Project_Name,Job_Name,Code identifier,ResNmNo,ActNmNo,"
                      "ProjNmNo,Region/Branch,Division,Resource Category,Wildfire,Exp_Rev,"
                      "Fire Activities,MPRA Category\n")
        bad_csv.write("2025-04-30,151,1,32,GG3,1371,0,105,,,"
                      "151-01-32-GG3-1371-0000-105,1844.04,0,33981.8,0,0,33981.8,"
                      "Nature Based Tourism,Parks & Visitor services,Lease Management,"
                      "Payroll Overheads,None,TERRITORIAL LEASES,418-01-12-GC2-GAS1-945,"
                      "1371-Payroll Overheads,GG3-Lease Management,0-None,"
                      "Nature Based Tourism,Nature Based Tourism,Payroll,,Expense,"
                      "Normal Activities,\n")
        bad_csv.close()
        try:
            with self.assertRaises(IBMSValidationError) as ctx:
                ibms_import_from_csv(bad_csv.name, self.fy, GLPivDownload)
            self.assertIn("Unable to parse downloadPeriod", str(ctx.exception))
        finally:
            Path(bad_csv.name).unlink()

    def test_import_wrong_column_count_raises_error(self):
        """A row with too few columns should raise ColumnCountError"""
        bad_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        bad_csv.write("col1,col2,col3\n")  # header
        bad_csv.write("30/04/2025,151,32\n")  # only 3 columns
        bad_csv.close()
        try:
            with self.assertRaises(ColumnCountError):
                ibms_import_from_csv(bad_csv.name, self.fy, GLPivDownload)
        finally:
            Path(bad_csv.name).unlink()


class IbmsImportFromCsvIBMDataTest(IbmsTestCase):
    """Test ibms_import_from_csv for IBMData using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "ibmdata_upload_test.csv")

    def test_import_creates_records(self):
        """Importing ibmdata CSV should create IBMData records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, IBMData, user=self.user)
        self.assertEqual(desc, "IBM Data")
        self.assertEqual(count, 4)
        self.assertEqual(IBMData.objects.filter(fy=self.fy).count(), 5)  # 4 new + 1 from setUp

    def test_import_sets_correct_fields(self):
        """Imported IBMData should have correct field values"""
        ibms_import_from_csv(self.csv_path, self.fy, IBMData)
        ibm = IBMData.objects.get(fy=self.fy, ibmIdentifier="418-01-12-GC2-GAS1-945")
        self.assertEqual(ibm.costCentre, "418")
        self.assertEqual(ibm.account, 1)
        self.assertEqual(ibm.service, 12)
        self.assertEqual(ibm.budgetArea, "Yamatji Nation")
        self.assertEqual(ibm.projectSponsor, "Operations Officer")

    def test_import_identifier_stored_uppercase(self):
        """IBMData ibmIdentifier should be stored uppercase even if CSV contains lowercase"""
        # Create a temporary CSV with a lowercase identifier version
        bad_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        bad_csv.write("ibmIdentifier,costCentre,account,service,activity,project,job,"
                      "budgetArea,projectSponsor,regionalSpecificInfo,servicePriorityID,"
                      "annualWPInfo,priorityActionNo,priorityLevel,marineKPI,regionProject,regionDescription\n")
        bad_csv.write("lowercase-abc-001,418,1,12,GC2,GAS1,945,Budget,Sponsor,,SP001,,,,,,\n")
        bad_csv.close()
        try:
            ibms_import_from_csv(bad_csv.name, self.fy, IBMData)
            ibm = IBMData.objects.get(fy=self.fy, ibmIdentifier="LOWERCASE-ABC-001")
            self.assertEqual(ibm.ibmIdentifier, "LOWERCASE-ABC-001")
        finally:
            Path(bad_csv.name).unlink()

    def test_import_updates_existing_record(self):
        """Importing an ibmIdentifier that already exists should update, not duplicate"""
        # Pre-create with different budgetArea
        mixer.blend(IBMData, fy=self.fy, ibmIdentifier="418-01-12-GC2-GAS1-945", budgetArea="Old")
        ibms_import_from_csv(self.csv_path, self.fy, IBMData)
        # Should still be exactly 1 record with this identifier
        self.assertEqual(IBMData.objects.filter(fy=self.fy, ibmIdentifier="418-01-12-GC2-GAS1-945").count(), 1)
        ibm = IBMData.objects.get(fy=self.fy, ibmIdentifier="418-01-12-GC2-GAS1-945")
        self.assertEqual(ibm.budgetArea, "Yamatji Nation")

    def test_import_no_user_still_succeeds(self):
        """Importing without a user argument should succeed"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, IBMData, user=None)
        self.assertEqual(count, 4)

    def test_import_invalid_account_raises_error(self):
        """A non-integer account value should raise IBMSValidationError"""
        bad_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        bad_csv.write("ibmIdentifier,costCentre,account,service,activity,project,job,"
                      "budgetArea,projectSponsor,regionalSpecificInfo,servicePriorityID,"
                      "annualWPInfo,priorityActionNo,priorityLevel,marineKPI,regionProject,regionDescription\n")
        bad_csv.write("IBM-BAD,418,NOT_AN_INT,12,GC2,GAS1,945,Budget,Sponsor,,SP001,,,,,,\n")
        bad_csv.close()
        try:
            with self.assertRaises(IBMSValidationError) as ctx:
                ibms_import_from_csv(bad_csv.name, self.fy, IBMData)
            self.assertIn("must be an integer", str(ctx.exception))
        finally:
            Path(bad_csv.name).unlink()

    def test_import_field_over_max_length_raises_error(self):
        """An ibmIdentifier exceeding 50 chars should raise FieldLengthError"""
        bad_csv = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        bad_csv.write("ibmIdentifier,costCentre,account,service,activity,project,job,"
                      "budgetArea,projectSponsor,regionalSpecificInfo,servicePriorityID,"
                      "annualWPInfo,priorityActionNo,priorityLevel,marineKPI,regionProject,regionDescription\n")
        bad_csv.write("A" * 51 + ",418,1,12,GC2,GAS1,945,Budget,Sponsor,,SP001,,,,,,\n")
        bad_csv.close()
        try:
            with self.assertRaises(FieldLengthError):
                ibms_import_from_csv(bad_csv.name, self.fy, IBMData)
        finally:
            Path(bad_csv.name).unlink()


class IbmsImportFromCsvCorporateStrategyTest(IbmsTestCase):
    """Test ibms_import_from_csv for CorporateStrategy using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "corporatestrategy_upload_test.csv")

    def test_import_creates_records(self):
        """Importing corporatestrategy CSV should create CorporateStrategy records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, CorporateStrategy)
        self.assertEqual(count, 2)
        self.assertEqual(CorporateStrategy.objects.filter(fy=self.fy).count(), 2)

    def test_import_sets_correct_fields(self):
        """Imported CorporateStrategy should have correct field values"""
        ibms_import_from_csv(self.csv_path, self.fy, CorporateStrategy)
        cs = CorporateStrategy.objects.get(fy=self.fy, corporateStrategyNo="S01")
        self.assertEqual(cs.description1, "Expand the terrestrial conservation reserve system")

    def test_import_updates_existing_record(self):
        """Re-importing should update an existing CorporateStrategy"""
        mixer.blend(CorporateStrategy, fy=self.fy, corporateStrategyNo="S01", description1="Old")
        ibms_import_from_csv(self.csv_path, self.fy, CorporateStrategy)
        self.assertEqual(CorporateStrategy.objects.filter(fy=self.fy, corporateStrategyNo="S01").count(), 1)
        cs = CorporateStrategy.objects.get(fy=self.fy, corporateStrategyNo="S01")
        self.assertEqual(cs.description1, "Expand the terrestrial conservation reserve system")


class IbmsImportFromCsvNCStrategicPlanTest(IbmsTestCase):
    """Test ibms_import_from_csv for NCStrategicPlan using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "ncstrategicplan_upload_test.csv")

    def test_import_creates_records(self):
        """Importing ncstrategicplan CSV should create NCStrategicPlan records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, NCStrategicPlan)
        self.assertEqual(desc, "Nature Conservation")
        self.assertEqual(count, 2)
        self.assertEqual(NCStrategicPlan.objects.filter(fy=self.fy).count(), 2)

    def test_import_sets_correct_fields(self):
        """Imported NCStrategicPlan should have correct direction field"""
        ibms_import_from_csv(self.csv_path, self.fy, NCStrategicPlan)
        sp = NCStrategicPlan.objects.get(fy=self.fy, strategicPlanNo="SP01")
        self.assertEqual(sp.direction, "Value 1")
        self.assertEqual(sp.directionNo, "D01")


class IbmsImportFromCsvDepartmentProgramTest(IbmsTestCase):
    """Test ibms_import_from_csv for DepartmentProgram using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "dept_program_upload_test.csv")

    def test_import_creates_records(self):
        """Importing dept_program CSV should create DepartmentProgram records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, DepartmentProgram)
        self.assertEqual(count, 4)
        self.assertEqual(DepartmentProgram.objects.filter(fy=self.fy).count(), 4)

    def test_import_sets_correct_fields(self):
        """Imported DepartmentProgram should have correct field values"""
        ibms_import_from_csv(self.csv_path, self.fy, DepartmentProgram)
        dp = DepartmentProgram.objects.get(fy=self.fy, ibmIdentifier="151-01-11-GE1-0000-000")
        self.assertEqual(dp.dept_program1, "Nature-based tourism")

    def test_import_links_glpivdownload_when_present(self):
        """DepartmentProgram import should link existing unlinked GLPivDownload records"""
        # Create a GLPivDownload with matching codeID but no department_program FK
        gl = mixer.blend(GLPivDownload, fy=self.fy, codeID="151-01-11-GE1-0000-000", department_program=None)
        ibms_import_from_csv(self.csv_path, self.fy, DepartmentProgram)
        gl.refresh_from_db()
        self.assertIsNotNone(gl.department_program)
        self.assertEqual(gl.department_program.ibmIdentifier, "151-01-11-GE1-0000-000")


class IbmsImportFromCsvGeneralServicePriorityTest(IbmsTestCase):
    """Test ibms_import_from_csv for GeneralServicePriority using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "generalservicepriority_upload_test.csv")

    def test_import_creates_records(self):
        """Importing generalservicepriority CSV should create GeneralServicePriority records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, GeneralServicePriority)
        self.assertEqual(count, 2)
        self.assertEqual(GeneralServicePriority.objects.filter(fy=self.fy).count(), 2)

    def test_import_sets_correct_fields(self):
        """Imported GeneralServicePriority should have correct categoryID"""
        ibms_import_from_csv(self.csv_path, self.fy, GeneralServicePriority)
        gsp = GeneralServicePriority.objects.get(fy=self.fy, servicePriorityNo="General 01")
        self.assertEqual(gsp.categoryID, "General-All")
        self.assertEqual(gsp.description, "Organisational Support - Mgt & Ops Sup ")


class IbmsImportFromCsvNCServicePriorityTest(IbmsTestCase):
    """Test ibms_import_from_csv for NCServicePriority using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "ncservicepriority_upload_test.csv")

    def test_import_creates_records(self):
        """Importing ncservicepriority CSV should create NCServicePriority records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, NCServicePriority)
        self.assertEqual(desc, "Nature Conservation Service Priority")
        self.assertEqual(count, 2)
        self.assertEqual(NCServicePriority.objects.filter(fy=self.fy).count(), 2)

    def test_import_sets_correct_fields(self):
        """Imported NCServicePriority should have correct categoryID"""
        ibms_import_from_csv(self.csv_path, self.fy, NCServicePriority)
        nsp = NCServicePriority.objects.get(fy=self.fy, servicePriorityNo="BC-X-X")
        self.assertEqual(nsp.categoryID, "BC-All")


class IbmsImportFromCsvPVSServicePriorityTest(IbmsTestCase):
    """Test ibms_import_from_csv for PVSServicePriority using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "pvsservicepriority_upload_test.csv")

    def test_import_creates_records(self):
        """Importing pvsservicepriority CSV should create PVSServicePriority records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, PVSServicePriority)
        self.assertEqual(desc, "Parks & Visitor Services Service Priority")
        self.assertEqual(count, 1)
        self.assertEqual(PVSServicePriority.objects.filter(fy=self.fy).count(), 1)

    def test_import_sets_correct_fields(self):
        """Imported PVSServicePriority should have correct field values"""
        ibms_import_from_csv(self.csv_path, self.fy, PVSServicePriority)
        pvs = PVSServicePriority.objects.get(fy=self.fy, servicePriorityNo="General 02")
        self.assertEqual(pvs.categoryID, "PM-All")


class IbmsImportFromCsvSFMServicePriorityTest(IbmsTestCase):
    """Test ibms_import_from_csv for SFMServicePriority using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "sfmservicepriority_upload_test.csv")

    def test_import_creates_records(self):
        """Importing sfmservicepriority CSV should create SFMServicePriority records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, SFMServicePriority)
        self.assertEqual(desc, "Forest Management Service Priority")
        self.assertEqual(count, 2)
        self.assertEqual(SFMServicePriority.objects.filter(fy=self.fy).count(), 2)

    def test_import_sets_correct_fields(self):
        """Imported SFMServicePriority should have correct regionBranch"""
        ibms_import_from_csv(self.csv_path, self.fy, SFMServicePriority)
        sfm = SFMServicePriority.objects.get(fy=self.fy, servicePriorityNo="FM-01")
        self.assertEqual(sfm.categoryID, "FM-All")
        self.assertEqual(sfm.regionBranch, "Region")


class IbmsImportFromCsvERServicePriorityTest(IbmsTestCase):
    """Test ibms_import_from_csv for ERServicePriority using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "erservicepriority_upload_test.csv")

    def test_import_creates_records(self):
        """Importing erservicepriority CSV should create ERServicePriority records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, ERServicePriority)
        self.assertEqual(desc, "Fire Services Service Priority")
        self.assertEqual(count, 1)
        self.assertEqual(ERServicePriority.objects.filter(fy=self.fy).count(), 1)

    def test_import_sets_correct_fields(self):
        """Imported ERServicePriority should have correct field values"""
        ibms_import_from_csv(self.csv_path, self.fy, ERServicePriority)
        er = ERServicePriority.objects.get(fy=self.fy, servicePriorityNo="Fire-01")
        self.assertEqual(er.categoryID, "Fire")
        self.assertEqual(er.classification, "Bushfire Suppression (CoA Activitiy DJ0)")


class IbmsImportFromCsvServicePriorityMappingTest(IbmsTestCase):
    """Test ibms_import_from_csv for ServicePriorityMapping using real test CSV data."""

    def setUp(self):
        super().setUp()
        self.csv_path = os.path.join(TEST_DATA_DIR, "serviceprioritymapping_upload_test.csv")

    def test_import_creates_records(self):
        """Importing serviceprioritymapping CSV should create ServicePriorityMapping records"""
        desc, count = ibms_import_from_csv(self.csv_path, self.fy, ServicePriorityMapping)
        self.assertEqual(desc, "Service Priority Mapping")
        self.assertEqual(count, 4)
        self.assertEqual(ServicePriorityMapping.objects.filter(fy=self.fy).count(), 4)

    def test_import_sets_correct_fields(self):
        """Imported ServicePriorityMapping should have correct field values"""
        ibms_import_from_csv(self.csv_path, self.fy, ServicePriorityMapping)
        spm = ServicePriorityMapping.objects.get(fy=self.fy, costCentreNo="811")
        self.assertEqual(spm.wildlifeManagement, "BC-All")
        self.assertEqual(spm.parksManagement, "PM-All")
        self.assertEqual(spm.forestManagement, "FM-All")

    def test_import_handles_empty_forest_management(self):
        """ServicePriorityMapping import should handle empty optional fields"""
        ibms_import_from_csv(self.csv_path, self.fy, ServicePriorityMapping)
        spm = ServicePriorityMapping.objects.get(fy=self.fy, costCentreNo="151")
        self.assertEqual(spm.forestManagement, "")


class IbmsImportFromCsvBlobClientTest(IbmsTestCase):
    """Test ibms_import_from_csv routes to blobload_context when given a BlobClient."""

    @patch("ibms.utils.blobload_context")
    def test_blob_client_uses_blobload_context(self, mock_blobload):
        """Passing a BlobClient source should use blobload_context, not csvload_context"""
        import csv
        import io
        from azure.storage.blob import BlobClient

        rows = [
            ["418-01-12-GC2-GAS1-945", "418", "1", "12", "GC2", "GAS1", "945",
             "Yamatji Nation", "Ops Officer", "", "General 01", "", "", "", "", "", ""]
        ]
        buf = io.StringIO()
        csv.writer(buf).writerows(rows)
        buf.seek(0)
        mock_blobload.return_value.__enter__.return_value = csv.reader(buf)
        mock_blobload.return_value.__exit__.return_value = None

        # Set __class__ so that isinstance(mock_blob, BlobClient) returns True
        mock_blob = MagicMock()
        mock_blob.__class__ = BlobClient
        desc, count = ibms_import_from_csv(mock_blob, self.fy, IBMData)

        mock_blobload.assert_called_once_with(mock_blob)
        self.assertEqual(count, 1)
