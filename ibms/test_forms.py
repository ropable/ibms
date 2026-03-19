from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from mixer.backend.django import mixer

from ibms.forms import ClearGLPivotForm, UploadForm
from ibms.tests import IbmsTestCase
from sfm.models import FinancialYear


class UploadFormTest(IbmsTestCase):
    """Tests for UploadForm validation."""

    def test_upload_form_required_fields(self):
        """UploadForm should require financial_year and file"""
        form = UploadForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("financial_year", form.errors)
        self.assertIn("upload_file", form.errors)

    def test_upload_form_financial_year_required(self):
        """UploadForm should require financial_year selection"""
        csv_file = SimpleUploadedFile("test.csv", b"data", content_type="text/csv")
        form = UploadForm(data={"upload_file_type": "ibm_data"}, files={"upload_file": csv_file})
        self.assertFalse(form.is_valid())
        self.assertIn("financial_year", form.errors)

    def test_upload_form_file_required(self):
        """UploadForm should require file upload"""
        fy = mixer.blend(FinancialYear, financialYear="2024/25")
        form = UploadForm(
            data={
                "upload_file_type": "ibm_data",
                "financial_year": fy.pk,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("upload_file", form.errors)

    def test_upload_form_csv_validation_rejects_json(self):
        """UploadForm should reject JSON files"""
        fy = mixer.blend(FinancialYear, financialYear="2024/25")
        json_file = SimpleUploadedFile("test.json", b'{"test": "data"}', content_type="application/json")

        form = UploadForm(
            data={
                "upload_file_type": "ibm_data",
                "financial_year": fy.pk,
            },
            files={"upload_file": json_file},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("upload_file", form.errors)
        self.assertIn("File type is not allowed", str(form.errors["upload_file"]))

    def test_upload_form_all_file_types_available(self):
        """UploadForm should include all documented file types"""
        form = UploadForm()
        choices_text = str(form.fields["upload_file_type"].choices)

        # Verify major file types are present
        self.assertIn("gl_pivot_download", choices_text)
        self.assertIn("ibm_data", choices_text)
        self.assertIn("corp_strategy", choices_text)
        self.assertIn("nature_conservation", choices_text)
        self.assertIn("dept_program", choices_text)

    def test_upload_form_file_type_required(self):
        """UploadForm should require file type selection"""
        fy = mixer.blend(FinancialYear, financialYear="2024/25")
        csv_file = SimpleUploadedFile("test.csv", b"data", content_type="text/csv")

        form = UploadForm(
            data={
                "upload_file_type": "",  # Empty choice
                "financial_year": fy.pk,
            },
            files={"upload_file": csv_file},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("upload_file_type", form.errors)

    def test_upload_form_financial_year_queryset(self):
        """UploadForm should include all available financial years"""
        fy1 = mixer.blend(FinancialYear, financialYear="2024/25")
        fy2 = mixer.blend(FinancialYear, financialYear="2023/24")

        form = UploadForm()
        fy_queryset = form.fields["financial_year"].queryset

        self.assertEqual(fy_queryset.count(), 2)
        self.assertIn(fy1, fy_queryset)
        self.assertIn(fy2, fy_queryset)

    def test_upload_form_financial_year_ordered_descending(self):
        """UploadForm should order financial years in descending order"""
        fy1 = mixer.blend(FinancialYear, financialYear="2022/23")
        fy2 = mixer.blend(FinancialYear, financialYear="2024/25")
        fy3 = mixer.blend(FinancialYear, financialYear="2023/24")

        form = UploadForm()
        fy_values = list(form.fields["financial_year"].queryset.values_list("financialYear", flat=True))

        # Should be in descending order
        self.assertEqual(fy_values[0], "2024/25")
        self.assertEqual(fy_values[1], "2023/24")
        self.assertEqual(fy_values[2], "2022/23")


class ClearGLPivotFormTest(IbmsTestCase):
    """Tests for ClearGLPivotForm validation."""

    def test_clear_glpivot_form_financial_year_required(self):
        """ClearGLPivotForm should require financial year"""
        form = ClearGLPivotForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("financial_year", form.errors)

    def test_clear_glpivot_form_financial_year_queryset_populated(self):
        """ClearGLPivotForm should include available financial years"""
        fy1 = mixer.blend(FinancialYear, financialYear="2024/25")
        fy2 = mixer.blend(FinancialYear, financialYear="2023/24")

        form = ClearGLPivotForm()
        fy_queryset = form.fields["financial_year"].queryset

        self.assertGreaterEqual(fy_queryset.count(), 2)
        self.assertIn(fy1, fy_queryset)
        self.assertIn(fy2, fy_queryset)

    def test_clear_glpivot_form_valid_submission(self):
        """ClearGLPivotForm should be valid with financial year"""
        fy = mixer.blend(FinancialYear, financialYear="2024/25")

        form = ClearGLPivotForm(
            data={
                "financial_year": fy.pk,
                "confirm": "Confirm",
            }
        )
        self.assertTrue(form.is_valid())

    def test_clear_glpivot_form_financial_year_ordered_descending(self):
        """ClearGLPivotForm should order financial years descending"""
        fy1 = mixer.blend(FinancialYear, financialYear="2022/23")
        fy2 = mixer.blend(FinancialYear, financialYear="2024/25")
        fy3 = mixer.blend(FinancialYear, financialYear="2023/24")

        form = ClearGLPivotForm()
        fy_values = list(form.fields["financial_year"].queryset.values_list("financialYear", flat=True))

        # Should be in descending order
        self.assertEqual(fy_values[0], "2024/25")
        self.assertEqual(fy_values[1], "2023/24")


class HelperFormBaseTest(TestCase):
    """Tests for HelperForm base class behavior."""

    def test_upload_form_has_crispy_helper(self):
        """UploadForm should have FormHelper for crispy forms"""
        form = UploadForm()
        self.assertTrue(hasattr(form, "helper"))
        self.assertIsNotNone(form.helper)

    def test_clear_glpivot_form_has_crispy_helper(self):
        """ClearGLPivotForm should have FormHelper"""
        form = ClearGLPivotForm()
        self.assertTrue(hasattr(form, "helper"))
        self.assertIsNotNone(form.helper)

    def test_upload_form_helper_form_class(self):
        """UploadForm helper should have form-horizontal class"""
        form = UploadForm()
        self.assertEqual(form.helper.form_class, "form-horizontal")

    def test_upload_form_helper_label_class(self):
        """UploadForm helper should have label sizing classes"""
        form = UploadForm()
        self.assertIn("col-", form.helper.label_class)

    def test_upload_form_helper_field_class(self):
        """UploadForm helper should have field sizing classes"""
        form = UploadForm()
        self.assertIn("col-", form.helper.field_class)
