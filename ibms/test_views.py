import os
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
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


class IbmsViewsTest(IbmsTestCase):
    """Test the ibms app views load ok."""

    client = Client()
    test_data_path = os.path.join("ibms", "test_data")

    def test_homepage_superuser(self):
        """Test homepage view contains required elements for a superuser"""
        url = reverse("site_home")
        self.client.login(username="admin", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "site_home.html")
        self.assertContains(response, 'id="superuser_upload"')

    def test_homepage_user(self):
        """Site homepage view should not contain some elements for a normal user"""
        url = reverse("site_home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "site_home.html")
        self.assertNotContains(response, '<li id="superuser_upload">')

    def test_ibms_views_get(self):
        """Test that all the 'normal user' IBMS views respond"""
        for view in [
            "download",
            "download_enhanced",
            "code_update",
            "data_amendment_list",
        ]:
            url = reverse(f"ibms:{view}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_ibms_views_req_auth(self):
        """Test that all the IBMS views will redirect a non-auth'ed user"""
        self.client.logout()
        for view in [
            "upload",
            "download",
            "download_enhanced",
            "code_update",
            "code_update_admin",
            "data_amendment_list",
        ]:
            url = reverse(f"ibms:{view}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_superuser_views_redirect(self):
        """Test superuser-only views redirects normal users"""
        self.client.logout()
        self.client.login(username="testuser", password="test")
        for view in [
            "upload",
            "download_dept_program",
            "code_update_admin",
            "clearglpivot",
        ]:
            url = reverse(f"ibms:{view}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_superuser_views_get(self):
        """Test superuser-only views load"""
        self.client.login(username="admin", password="test")
        for view in [
            "upload",
            "download_dept_program",
            "code_update_admin",
            "clearglpivot",
        ]:
            url = reverse(f"ibms:{view}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_upload_ibmdata_post(self):
        """Test a valid CSV upload for IBM data."""
        # Start with one IBMData object.
        self.assertEqual(IBMData.objects.count(), 1)
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "ibmdata_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("ibmdata_upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "ibm_data", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        # Conclude with 5 IBMData objects.
        self.assertEqual(IBMData.objects.count(), 5)

    def test_upload_glpivot_post(self):
        """Test a valid CSV upload for GL pivot download data."""
        # Start with zero GLPivDownload objects.
        self.assertEqual(GLPivDownload.objects.count(), 0)
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "glpivot_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("glpivot_upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "gl_pivot_download", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        # Conclude with 4 GLPivDownload objects.
        self.assertEqual(GLPivDownload.objects.count(), 4)

    def test_clear_glpivot_post(self):
        """Test the superuser-only view to clear GLPivDownload data for a given financial year."""
        self.client.login(username="admin", password="test")
        # Start with some GLPivDownload data.
        mixer.blend(GLPivDownload, fy=self.fy)
        self.assertTrue(GLPivDownload.objects.exists())
        url = reverse("ibms:clearglpivot")
        resp = self.client.post(url, data={"financial_year": self.fy.financialYear}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Conclude with no GLPivDownload data.
        self.assertFalse(GLPivDownload.objects.exists())

    def test_upload_view_glpivot_fk_links(self):
        """Following upload of GL pivot download data, confirm that a FK link to IBM data records are made."""
        url = reverse("ibms:upload")
        # Upload IBMData and GLPivDownload records.
        with open(os.path.join(self.test_data_path, "ibmdata_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("ibmdata_upload.csv", test_data.read())
            _ = self.client.post(
                url, data={"upload_file_type": "ibm_data", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        with open(os.path.join(self.test_data_path, "glpivot_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("glpivot_upload.csv", test_data.read())
            _ = self.client.post(
                url, data={"upload_file_type": "gl_pivot_download", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        # All of the GLPivDownload objects will have a FK link to the matching IBMData objects.
        for gl in GLPivDownload.objects.all():
            self.assertTrue(gl.ibmdata)

    def test_upload_view_deptprogram_post(self):
        """Test a valid CSV upload for Department Program data."""
        # Prep: we need an IBMData record with a matching identifer.
        mixer.blend(
            IBMData,
            fy=self.fy,
            ibmIdentifier="151-01-11-GE1-0000-000",
        )
        # Start with zero DepartmentProgram objects.
        self.assertEqual(DepartmentProgram.objects.count(), 0)
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "dept_program_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("dept_program_upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "dept_program", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(DepartmentProgram.objects.count(), 4)

    def test_ibms_ajax_endpoints(self):
        """Test that the IBMS AJAX endpoints work"""
        for _ in range(20):
            mixer.blend(GLPivDownload, codeID=self.ibmdata.ibmIdentifier[0:29], downloadPeriod=date.today().strftime("%d/%m/%Y"))

        for endpoint in [
            "ajax_glpivdownload_financialyear",
            "ajax_ibmdata_costcentre",
            "ajax_glpivdownload_costcentre",
            "ajax_glpivdownload_regionbranch",
            "ajax_ibmdata_service",
            "ajax_ibmdata_project",
            "ajax_ibmdata_job",
            "ajax_ibmdata_budgetarea",
            "ajax_ibmdata_projectsponsor",
            "ajax_glpivdownload_division",
            "ajax_mappings",
        ]:
            url = reverse(f"ibms:{endpoint}")
            response = self.client.get(url, {"financialYear": self.fy.financialYear})
            self.assertEqual(response.status_code, 200)

    def test_data_amendment_list_filter(self):
        """Test that the DataAmendmentList view returns filtered records"""
        url = reverse("ibms:data_amendment_list")
        response = self.client.get(url, {"cost_centre": "999"})
        self.assertContains(response, self.ibmdata.ibmIdentifier)

    def test_data_amendment_list_rule_budgetarea(self):
        """Test the DataAmendmentList view business rule: filter out blank budgetArea"""
        ibmdata2 = mixer.blend(IBMData, fy=self.fy, costCentre="999", budgetArea="", activity="AB1", projectSponsor=self.fake.name())
        url = reverse("ibms:data_amendment_list")
        response = self.client.get(url, {"cost_centre": "999"})
        # The new IBMData record shouldn't be in the response.
        self.assertNotContains(response, ibmdata2.ibmIdentifier)
        self.assertContains(response, self.ibmdata.ibmIdentifier)

    def test_data_amendment_list_rule_dj0(self):
        """Test the DataAmendmentList view business rule: filter out activity DJ0"""
        ibmdata2 = mixer.blend(IBMData, fy=self.fy, costCentre="999", activity="DJ0", projectSponsor=self.fake.name())
        url = reverse("ibms:data_amendment_list")
        response = self.client.get(url, {"cost_centre": "999"})
        self.assertNotContains(response, ibmdata2.ibmIdentifier)
        self.assertContains(response, self.ibmdata.ibmIdentifier)

    def test_data_amendment_update_get(self):
        """Test that the DataAmendmentUpdate view responds"""
        url = reverse("ibms:data_amendment_update", kwargs={"pk": self.ibmdata.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_data_amendment_update_cancel(self):
        """Test the cancelling the DataAmendmentUpdate view redirects to the list view"""
        url = reverse("ibms:data_amendment_update", kwargs={"pk": self.ibmdata.pk})
        resp = self.client.post(url, {"cancel": "Cancel"})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("ibms:data_amendment_list"))

    def test_data_amendment_update_post(self):
        """Test that the DataAmendmentUpdate view responds correctly to a POST request"""
        url = reverse("ibms:data_amendment_update", kwargs={"pk": self.ibmdata.pk})
        response = self.client.post(url, {"budgetArea": "Operations"})
        self.assertEqual(response.status_code, 302)
        ibmdata = IBMData.objects.first()
        self.assertEqual(ibmdata.budgetArea, "Operations")

    def test_upload_corpstrategy_post(self):
        """Test a valid CSV upload for CorporateStrategy data."""
        self.assertFalse(CorporateStrategy.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "corporatestrategy_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "corp_strategy", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(CorporateStrategy.objects.exists())

    def test_upload_ncstrategicplan_post(self):
        """Test a valid CSV upload for NCStrategicPlan data."""
        self.assertFalse(NCStrategicPlan.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "ncstrategicplan_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "nature_conservation", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(NCStrategicPlan.objects.exists())

    def test_upload_generalservicepriority_post(self):
        """Test a valid CSV upload for GeneralServicePriority data."""
        self.assertFalse(GeneralServicePriority.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "generalservicepriority_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "general_sp", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(GeneralServicePriority.objects.exists())

    def test_upload_ncservicepriority_post(self):
        """Test a valid CSV upload for NCServicePriority data."""
        self.assertFalse(NCServicePriority.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "ncservicepriority_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "nc_sp", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(NCServicePriority.objects.exists())

    def test_upload_pvsservicepriority_post(self):
        """Test a valid CSV upload for PVSServicePriority data."""
        self.assertFalse(PVSServicePriority.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "pvsservicepriority_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "pvs_sp", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(PVSServicePriority.objects.exists())

    def test_upload_sfmservicepriority_post(self):
        """Test a valid CSV upload for SFMServicePriority data."""
        self.assertFalse(SFMServicePriority.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "sfmservicepriority_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "sfm_sp", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(SFMServicePriority.objects.exists())

    def test_upload_erservicepriority_post(self):
        """Test a valid CSV upload for ERServicePriority data."""
        self.assertFalse(ERServicePriority.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "erservicepriority_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "er_sp", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ERServicePriority.objects.exists())

    def test_upload_serviceprioritymapping_post(self):
        """Test a valid CSV upload for ServicePriorityMapping data."""
        self.assertFalse(ServicePriorityMapping.objects.exists())
        url = reverse("ibms:upload")
        with open(os.path.join(self.test_data_path, "serviceprioritymapping_upload_test.csv"), "rb") as test_data:
            upload = SimpleUploadedFile("upload.csv", test_data.read())
            resp = self.client.post(
                url, data={"upload_file_type": "service_priority_mapping", "upload_file": upload, "financial_year": "2024/25"}, follow=True
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ServicePriorityMapping.objects.exists())
