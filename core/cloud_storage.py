"""
Dual-Cloud Storage Engine: AWS S3 & GCP Cloud Storage with Automatic Failover.
Primary: AWS S3 (Bucket: vapi-recordings-kishor-tech)
Fallback: GCP Cloud Storage (Bucket: enterprise-rag-raw-kkp-53d8ce01)
"""

import os
import io
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("DualCloudStorage")


class DualCloudStorageManager:
    """Manages recording uploads and call artifacts with zero-downtime dual-cloud fallback."""

    def __init__(self):
        # AWS S3 Settings
        self.s3_bucket = os.getenv("AWS_S3_BUCKET", "vapi-recordings-kishor-tech")
        self.s3_region = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        # GCP Cloud Storage Settings
        self.gcp_bucket = os.getenv("GCP_STORAGE_BUCKET", "enterprise-rag-raw-kkp-53d8ce01")
        self.gcp_project = os.getenv("GCP_PROJECT_ID", "project-53d8ce01-b0e0-4f8b-94c")
        self.gcp_sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    def upload_call_artifact(
        self,
        data: bytes,
        filename: str,
        content_type: str = "audio/wav",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads audio recording or call transcript.
        Tries AWS S3 first; on any network/auth error, automatically falls back to GCP Cloud Storage.
        """
        metadata = metadata or {}

        # 1. Primary: AWS S3
        try:
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError

            s3_client = boto3.client(
                "s3",
                region_name=self.s3_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            key = f"recordings/{filename}"
            s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                Metadata=metadata
            )
            url = f"https://{self.s3_bucket}.s3.{self.s3_region}.amazonaws.com/{key}"
            logger.info(f"✅ [AWS S3] Uploaded artifact '{key}' to {self.s3_bucket}")
            return {
                "status": "success",
                "provider": "aws_s3",
                "bucket": self.s3_bucket,
                "key": key,
                "url": url,
                "is_fallback": False
            }
        except Exception as s3_err:
            logger.warning(f"⚠️ [AWS S3 Failed, Triggering GCP Fallback]: {s3_err}")

        # 2. Fallback: Google Cloud Storage (GCP)
        try:
            from google.cloud import storage
            from google.oauth2 import service_account

            if self.gcp_sa_json:
                sa_info = json.loads(self.gcp_sa_json)
                creds = service_account.Credentials.from_service_account_info(sa_info)
                gcs_client = storage.Client(credentials=creds, project=self.gcp_project)
            else:
                gcs_client = storage.Client(project=self.gcp_project)

            bucket = gcs_client.bucket(self.gcp_bucket)
            blob = bucket.blob(f"recordings/{filename}")
            blob.upload_from_string(data, content_type=content_type)
            gcs_url = f"https://storage.googleapis.com/{self.gcp_bucket}/recordings/{filename}"
            logger.info(f"🛡️ [GCP Cloud Storage Fallback] Uploaded artifact to {self.gcp_bucket}")
            return {
                "status": "success",
                "provider": "gcp_storage",
                "bucket": self.gcp_bucket,
                "key": f"recordings/{filename}",
                "url": gcs_url,
                "is_fallback": True,
                "fallback_reason": str(s3_err)
            }
        except Exception as gcp_err:
            logger.error(f"❌ [Dual-Cloud Storage Error] Both AWS S3 and GCP GCS failed: {gcp_err}")
            return {
                "status": "error",
                "message": f"Storage upload failed across both providers. S3: {s3_err} | GCP: {gcp_err}"
            }


cloud_storage_manager = DualCloudStorageManager()
