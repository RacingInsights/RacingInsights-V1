from pprint import pprint
import unittest

import boto3

from previous_versions.Version_Before_Refactor.src.backend.aws.credentials import Credentials, app_client_id, region
from previous_versions.Version_Before_Refactor.src.backend.aws.relative_estimation_data import RelativeEstimationDataDBLink
from previous_versions.Version_Before_Refactor.tests.utils.disable_resource_warnings import ignore_warnings


def initialize_relative_estimation_data_object():
    # Needs: RelativeEstimationDataDBLink instance
    relative_estimation_data = RelativeEstimationDataDBLink()

    # Needs to set the resource
    # First, get the credentials
    cognito = boto3.client('cognito-idp', region_name=region)
    cognito_idp_response = cognito.initiate_auth(
            ClientId=app_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': "gogotibke@hotmail.com",
                'PASSWORD': "testPw1234_"
            }
    )
    credentials = Credentials(cognito_idp_response=cognito_idp_response)  # Get the AWS credentials
    relative_estimation_data.set_resource(credentials=credentials)

    return relative_estimation_data


class TestRelativeEstimationData(unittest.TestCase):

    @ignore_warnings
    def test_get_relative_estimation_data(self):
        relative_estimation_data = initialize_relative_estimation_data_object()

        data = relative_estimation_data.get_relative_estimation_data(track_id=69, car_class=34)
        pprint(data)
