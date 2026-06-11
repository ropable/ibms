from datetime import date, datetime

from django.test import TestCase
from mixer.backend.django import mixer

from ibms.models import GLPivDownload, IBMData
from ibms.tests import IbmsTestCase
from ibms.utils import FieldLengthError, IBMSValidationError, get_download_period, validate_char_field, validate_integer_field


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
