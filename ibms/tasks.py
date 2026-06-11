import logging
import os
from typing import Tuple

from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django_tasks import task

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
from ibms.utils import ibms_import_from_csv
from sfm.models import FinancialYear

LOGGER = logging.getLogger("ibms")


@task
def process_uploaded_csv(blob_name: str, fy: str, file_type: str, username: str) -> Tuple[str, str, int, str]:
    """Download a CSV blob from Azure Blob Storage, count its data rows, and log the result."""
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        LOGGER.error("process_uploaded_csv: AZURE_STORAGE_CONNECTION_STRING is not set")
        return None

    container_name = settings.AZURE_STORAGE_CONTAINER_NAME

    blob_service = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    financial_year = FinancialYear.objects.get(financialYear=fy)
    user = User.objects.get(username=username)
    model_type = "Unknown"
    record_count = 0

    try:
        if file_type == "gl_pivot_download":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, GLPivDownload)
        elif file_type == "ibm_data":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, IBMData, user)
        elif file_type == "corp_strategy":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, CorporateStrategy)
        elif file_type == "nature_conservation":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, NCStrategicPlan)
        elif file_type == "dept_program":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, DepartmentProgram)
        elif file_type == "general_sp":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, GeneralServicePriority)
        elif file_type == "nc_sp":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, NCServicePriority)
        elif file_type == "pvs_sp":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, PVSServicePriority)
        elif file_type == "sfm_sp":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, SFMServicePriority)
        elif file_type == "er_sp":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, ERServicePriority)
        elif file_type == "service_priority_mapping":
            model_type, record_count = ibms_import_from_csv(blob_client, financial_year, ServicePriorityMapping)

        # Send a notification email to the user who uploaded the file on success.
        LOGGER.info(
            f"Sending an email to {user.email}: processed {file_type} upload {blob_client.blob_name} ({record_count} {model_type} records)"
        )
        msg = EmailMultiAlternatives(
            subject=f"Processed IBMS {file_type} upload: {blob_client.blob_name}",
            body=f"Successfully processed IBMS {file_type} upload {blob_client.blob_name} ({record_count} {model_type} records)",
            from_email=settings.NOREPLY_EMAIL,
            to=[user.email],
        )
        msg.send(fail_silently=True)
    except Exception as e:
        LOGGER.warning(e)
        # Send a notification email to the user who uploaded the file on failure.
        LOGGER.info(f"Sending an email to {user.email}: failure processing uploaded file {blob_client.blob_name}")
        msg = EmailMultiAlternatives(
            subject=f"Failed processing IBMS {file_type} upload {blob_client.blob_name}: {blob_client.blob_name}",
            body=f"Failed to process IBMS {file_type} upload {blob_client.blob_name}\n{e}",
            from_email=settings.NOREPLY_EMAIL,
            to=[user.email],
        )
        msg.send(fail_silently=True)
        raise
    finally:
        # Remove (delete) the uploaded CSV from blob storage.
        blob_client.delete_blob()
        LOGGER.info(f"Deleted uploaded file {blob_client.blob_name}")

    return blob_name, model_type, record_count, user.email
