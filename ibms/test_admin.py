from django.test.client import Client
from django.urls import reverse

from ibms.tests import IbmsTestCase


class IbmsAdminTest(IbmsTestCase):
    client = Client()

    def setUp(self):
        super().setUp()
        self.client.login(username="admin", password="test")

    def test_admin_changelist_views(self):
        for model in [
            "ibmdata",
            "departmentprogram",
            "glpivdownload",
            "corporatestrategy",
            "ncstrategicplan",
            "generalservicepriority",
            "ncservicepriority",
            "pvsservicepriority",
            "sfmservicepriority",
            "erservicepriority",
            "serviceprioritymapping",
        ]:
            url = reverse(f"admin:ibms_{model}_changelist")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_admin_change_views(self):
        url = reverse("admin:ibms_ibmdata_change", kwargs={"object_id": self.ibmdata.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_export_as_csv_action(self):
        changelist_url = reverse("admin:ibms_ibmdata_changelist")
        response = self.client.post(changelist_url, {"action": "export_as_csv", "_selected_action": [self.ibmdata.pk]}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
