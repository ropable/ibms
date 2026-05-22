from django.test.client import Client
from mixer.backend.django import mixer

from ibms.models import DepartmentProgram, GeneralServicePriority, GLPivDownload, IBMData
from ibms.tests import IbmsTestCase


class IBMDataTest(IbmsTestCase):
    """Tests for IBMData model methods and save behavior."""

    client = Client()

    def test_get_service_priority_with_matches(self):
        """Test finding matching service priority in order of preference"""
        # Create a matching GeneralServicePriority
        sp = mixer.blend(
            GeneralServicePriority,
            fy=self.fy,
            servicePriorityNo=self.ibmdata.servicePriorityID,
        )

        result = self.ibmdata.get_service_priority()
        self.assertEqual(result.servicePriorityNo, sp.servicePriorityNo)

    def test_get_service_priority_no_match(self):
        """Test when no service priority exists"""
        self.ibmdata.servicePriorityID = "NONEXISTENT_SP"

        result = self.ibmdata.get_service_priority()
        self.assertIsNone(result)

    def test_get_service_priority_existing_link(self):
        """Test returning already-set service_priority"""
        sp = mixer.blend(
            GeneralServicePriority,
            fy=self.fy,
            servicePriorityNo=self.ibmdata.servicePriorityID,
        )
        self.ibmdata.service_priority = sp
        self.ibmdata.save()

        result = self.ibmdata.get_service_priority()
        self.assertEqual(result, sp)

    def test_save_auto_links_service_priority(self):
        """Verify save() automatically links service priority objects"""
        sp = mixer.blend(
            GeneralServicePriority,
            fy=self.fy,
            servicePriorityNo="TEST_SP_001",
        )
        new_ibm = mixer.blend(
            IBMData,
            fy=self.fy,
            servicePriorityID=sp.servicePriorityNo,
        )
        new_ibm.save()

        new_ibm.refresh_from_db()
        self.assertIsNotNone(new_ibm.content_type)
        self.assertIsNotNone(new_ibm.object_id)

    def test_get_account_display_with_zero_padding(self):
        """Test account display formatting"""
        self.ibmdata.account = 1
        self.ibmdata.save()
        self.assertEqual(self.ibmdata.get_account_display(), "01")
        self.assertEqual(len(self.ibmdata.get_account_display()), 2)

    def test_get_account_display_two_digits(self):
        """Test account display with 2-digit account"""
        self.ibmdata.account = 42
        self.assertEqual(self.ibmdata.get_account_display(), "42")

    def test_get_account_display_none(self):
        """Test account display returns empty string when None"""
        self.ibmdata.account = None
        self.assertEqual(self.ibmdata.get_account_display(), "")

    def test_get_service_display_with_zero_padding(self):
        """Test service display formatting"""
        self.ibmdata.service = 3
        self.assertEqual(self.ibmdata.get_service_display(), "03")

    def test_get_service_display_two_digits(self):
        """Test service display with 2-digit service"""
        self.ibmdata.service = 99
        self.assertEqual(self.ibmdata.get_service_display(), "99")

    def test_get_service_display_none(self):
        """Test service display returns empty string when None"""
        self.ibmdata.service = None
        self.assertEqual(self.ibmdata.get_service_display(), "")

    def test_get_project_display_with_zero_padding(self):
        """Test project display formatting"""
        self.ibmdata.project = "42"
        self.assertEqual(self.ibmdata.get_project_display(), "0042")

    def test_get_project_display_four_digits(self):
        """Test project display with 4-digit project"""
        self.ibmdata.project = "1234"
        self.assertEqual(self.ibmdata.get_project_display(), "1234")

    def test_get_project_display_none(self):
        """Test project display returns empty string when None"""
        self.ibmdata.project = None
        self.assertEqual(self.ibmdata.get_project_display(), "")

    def test_get_job_display_with_zero_padding(self):
        """Test job display formatting"""
        self.ibmdata.job = "5"
        self.assertEqual(self.ibmdata.get_job_display(), "005")

    def test_get_job_display_three_digits(self):
        """Test job display with 3-digit job"""
        self.ibmdata.job = "999"
        self.assertEqual(self.ibmdata.get_job_display(), "999")

    def test_get_region_branch_with_glpivdownload(self):
        """Test region branch retrieval from linked GLPivDownload"""
        gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            codeID=self.ibmdata.ibmIdentifier,
            regionBranch="Test Region",
        )

        self.assertEqual(self.ibmdata.get_region_branch(), "Test Region")

    def test_get_region_branch_without_glpivdownload(self):
        """Test empty string when no GLPivDownload exists"""
        self.assertEqual(self.ibmdata.get_region_branch(), "")

    def test_get_region_branch_with_multiple_glpivdownloads(self):
        """Test returns first GLPivDownload when multiple exist"""
        mixer.blend(
            GLPivDownload,
            fy=self.fy,
            codeID=self.ibmdata.ibmIdentifier,
            regionBranch="First Region",
        )
        mixer.blend(
            GLPivDownload,
            fy=self.fy,
            codeID=self.ibmdata.ibmIdentifier,
            regionBranch="Second Region",
        )

        self.assertEqual(self.ibmdata.get_region_branch(), "First Region")


class GLPivDownloadTest(IbmsTestCase):
    """Tests for GLPivDownload model methods and save behavior."""

    client = Client()

    def setUp(self):
        super().setUp()
        self.gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            downloadPeriod="15/03/2024",
            download_period=None,
            codeID=self.ibmdata.ibmIdentifier,
            account=5,
            project="42",
            job="7",
        )

    def test_save_auto_link_ibmdata(self):
        """Verify save() automatically links matching IBMData"""
        new_gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            codeID=self.ibmdata.ibmIdentifier,
            downloadPeriod="15/03/2024",
            ibmdata=None,
        )
        new_gl.save()

        new_gl.refresh_from_db()
        self.assertEqual(new_gl.ibmdata, self.ibmdata)

    def test_save_auto_link_ibmdata_not_found(self):
        """Verify save() leaves ibmdata None when no match"""
        new_gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            codeID="NONEXISTENT",
            downloadPeriod="15/03/2024",
            ibmdata=None,
        )
        new_gl.save()

        new_gl.refresh_from_db()
        self.assertIsNone(new_gl.ibmdata)

    def test_save_auto_link_department_program(self):
        """Verify save() automatically links DepartmentProgram"""
        dept = mixer.blend(
            DepartmentProgram,
            fy=self.fy,
            ibmIdentifier=self.ibmdata.ibmIdentifier,
        )
        new_gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            codeID=self.ibmdata.ibmIdentifier,
            downloadPeriod="15/03/2024",
            department_program=None,
        )
        new_gl.save()

        new_gl.refresh_from_db()
        self.assertEqual(new_gl.department_program, dept)

    def test_save_parse_download_period_date(self):
        """Verify save() parses downloadPeriod string to download_period date"""
        new_gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            downloadPeriod="15/03/2024",
            download_period=None,
        )
        new_gl.save()

        new_gl.refresh_from_db()
        self.assertEqual(new_gl.download_period.day, 15)
        self.assertEqual(new_gl.download_period.month, 3)
        self.assertEqual(new_gl.download_period.year, 2024)

    def test_save_date_parsing_invalid_format(self):
        """Verify save() handles invalid date format gracefully"""
        new_gl = mixer.blend(
            GLPivDownload,
            fy=self.fy,
            downloadPeriod="2024-03-15",  # Invalid format
            download_period=None,
        )
        new_gl.save()
        new_gl.refresh_from_db()
        self.assertIsNone(new_gl.download_period)

    def test_save_does_not_overwrite_existing_ibmdata_link(self):
        """Verify save() does not overwrite existing ibmdata link"""
        other_ibm = mixer.blend(
            IBMData,
            fy=self.fy,
        )
        self.gl.ibmdata = other_ibm
        self.gl.save()

        self.gl.refresh_from_db()
        self.assertEqual(self.gl.ibmdata, other_ibm)

    def test_get_ibmdata_found(self):
        """Verify get_ibmdata() returns matching IBMData"""
        result = self.gl.get_ibmdata()
        self.assertEqual(result, self.ibmdata)

    def test_get_ibmdata_not_found(self):
        """Verify get_ibmdata() returns None when no match"""
        self.gl.codeID = "NONEXISTENT"
        result = self.gl.get_ibmdata()
        self.assertIsNone(result)

    def test_get_department_program_found(self):
        """Verify get_department_program() returns matching object"""
        dept = mixer.blend(
            DepartmentProgram,
            fy=self.fy,
            ibmIdentifier=self.ibmdata.ibmIdentifier,
        )
        result = self.gl.get_department_program()
        self.assertEqual(result, dept)

    def test_get_department_program_not_found(self):
        """Verify get_department_program() returns None when no match"""
        self.gl.codeID = "NONEXISTENT"
        result = self.gl.get_department_program()
        self.assertIsNone(result)

    def test_get_account_display_zero_padding(self):
        """Account display should be zero-padded to 2 digits"""
        self.gl.account = 3
        self.assertEqual(self.gl.get_account_display(), "03")

    def test_get_account_display_two_digits(self):
        """Account display should remain 2 digits"""
        self.gl.account = 99
        self.assertEqual(self.gl.get_account_display(), "99")

    def test_get_project_display_zero_padding(self):
        """Project display should be zero-padded to 4 digits"""
        self.gl.project = "42"
        self.assertEqual(self.gl.get_project_display(), "0042")

    def test_get_project_display_four_digits(self):
        """Project display should remain 4 digits"""
        self.gl.project = "1234"
        self.assertEqual(self.gl.get_project_display(), "1234")

    def test_get_job_display_zero_padding(self):
        """Job display should be zero-padded to 3 digits"""
        self.gl.job = "5"
        self.assertEqual(self.gl.get_job_display(), "005")

    def test_get_job_display_three_digits(self):
        """Job display should remain 3 digits"""
        self.gl.job = "999"
        self.assertEqual(self.gl.get_job_display(), "999")
