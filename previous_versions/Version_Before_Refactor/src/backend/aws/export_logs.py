import logging
import os

import boto3

from previous_versions.Version_Before_Refactor.src.backend.aws.credentials import Credentials


class S3ResourceHandler:
    def __init__(self, log_id: str = None):
        self.s3_resource = None
        self.log_id = log_id
        self.name = 'racinginsights-app-log-bucket1'

    def set_resource(self, credentials: Credentials):
        self.s3_resource = boto3.resource('s3',
                                          aws_access_key_id=credentials.aws_access_key_id,
                                          aws_secret_access_key=credentials.aws_secret_access_key,
                                          aws_session_token=credentials.aws_session_token,
                                          region_name=credentials.region
                                          )

    def export_logs(self, log_file_name: str):
        """Code to send the log file to s3 resource"""
        logging.shutdown()  # Shut down logging to release the file handler

        # Upload the file to the S3 bucket using the resource. This upload overwrites already available file in bucket.
        # Hence, 1 file per user and always most recent log is available in bucket
        self.s3_resource.Bucket(self.name).upload_file(log_file_name, self.log_id)

        # Want to delete the file such that it's not visible for user
        if os.path.exists(log_file_name):
            os.remove(log_file_name)

        # Only the log_id is stored. Useful if user-specific debugging is required
        with open(log_file_name, 'w') as f:
            f.write(self.log_id)
