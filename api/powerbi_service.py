from urllib.parse import urlparse
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os
from django.conf import settings

def generate_sas_url_from_api(logo_url, expiry_hours=6):
    AZURE_STORAGE_ACCOUNT_NAME = "csenyone"
    AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_KEY
    AZURE_STORAGE_CONTAINER_NAME = "sfenyone"

    parsed_url = urlparse(logo_url)
    path_parts = parsed_url.path.lstrip("/").split("/", 1)
    if len(path_parts) < 2:
        return None
    
    blob_name = path_parts[1]

    expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)

    # Generate SAS token
    sas_token = generate_blob_sas(
        account_name=AZURE_STORAGE_ACCOUNT_NAME,
        container_name=AZURE_STORAGE_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=AZURE_STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time
    )

    sas_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER_NAME}/{blob_name}?{sas_token}"
    return sas_url
