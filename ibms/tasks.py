import logging
import os

from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.contrib.auth import get_user_model
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
def process_uploaded_csv(blob_name: str, fy: str, file_type: str, username: str) -> str | None:
    """Download a CSV blob from Azure Blob Storage, count its data rows, and log the result."""
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        LOGGER.error("process_uploaded_csv: AZURE_STORAGE_CONNECTION_STRING is not set")
        return

    container_name = settings.AZURE_STORAGE_CONTAINER_NAME

    blob_service = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    fy = FinancialYear.objects.get(financialYear=fy)

    if file_type == "gl_pivot_download":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, GLPivDownload)
    elif file_type == "ibm_data":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, IBMData)
    elif file_type == "corp_strategy":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, CorporateStrategy)
    elif file_type == "nature_conservation":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, NCStrategicPlan)
    elif file_type == "dept_program":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, DepartmentProgram)
    elif file_type == "general_sp":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, GeneralServicePriority)
    elif file_type == "nc_sp":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, NCServicePriority)
    elif file_type == "pvs_sp":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, PVSServicePriority)
    elif file_type == "sfm_sp":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, SFMServicePriority)
    elif file_type == "er_sp":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, ERServicePriority)
    elif file_type == "service_priority_mapping":
        data_type, record_count = ibms_import_from_csv(blob_client, fy, ServicePriorityMapping)
    else:
        raise Exception(f"process_upload_file : file type {file_type} unknown")

    # Send a notification email to the user who uploaded the file on success.
    User = get_user_model()
    user = User.objects.get(username=username)
    LOGGER.info(f"Sending an email to {user.email}: processed {file_type} upload ({record_count} records)")

    msg = EmailMultiAlternatives(
        subject=f"Processed IBMS {file_type} upload: {blob_client.blob_name}",
        body=f"Successfully processed IBMS {file_type} upload {blob_client.blob_name} ({record_count} records)",
        from_email=settings.NOREPLY_EMAIL,
        to=[user.email],
    )
    msg.send(fail_silently=True)

    # Remove (delete) the uploaded CSV from blob storage on success.
    blob_client.delete_blob()
    LOGGER.info(f"Deleted uploaded blob {blob_client.blob_name}")

    return data_type, record_count, user.email
