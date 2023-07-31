from dataclasses import dataclass

import boto3

from src.backend.AWS.addresses import AWSAddress
from src.backend.AWS.login import CognitoIDPToken


@dataclass
class AWSCredentials:
    """Contains the credentials needed for various interactions with AWS"""
    access_key_id: str
    secret_access_key: str
    session_token: str


class CognitoIdentityClient:
    """
    Class for interacting with a cognito identity client.
    Note: This is different from the cognito identity provider!
    """

    def __init__(self):
        self.client = boto3.client('cognito-identity', region_name=AWSAddress.REGION.value)

    def get_aws_credentials(self, idp_token: CognitoIDPToken) -> AWSCredentials:
        """Main method that returns the credentials needed when interacting with AWS clients/resources/services"""
        identity_id = self.get_aws_identity_id(idp_token=idp_token)
        credentials_response = self.get_aws_credentials_response(identity_id=identity_id, idp_token=idp_token)

        aws_credentials = AWSCredentials(access_key_id=credentials_response['Credentials']['AccessKeyId'],
                                         secret_access_key=credentials_response['Credentials']['SecretKey'],
                                         session_token=credentials_response['Credentials']['SessionToken'])
        return aws_credentials

    def get_aws_identity_id(self, idp_token: CognitoIDPToken):
        """Method that returns an AWS identity id. Required for getting credentials"""
        id_response = self.client.get_id(
                AccountId=AWSAddress.AWS_ACCOUNT_ID.value,
                IdentityPoolId=AWSAddress.IDENTITY_POOL_ID.value,
                Logins={
                    f"cognito-idp.{AWSAddress.REGION.value}.amazonaws.com/{AWSAddress.USER_POOL_ID.value}": idp_token
                }
        )
        return id_response['IdentityId']

    def get_aws_credentials_response(self, identity_id, idp_token: CognitoIDPToken):
        """
        Gets temporary credentials for interacting with AWS clients/resources/services.
        Note that this way it assumes a pre-defined role that can be assigned specific permissions
        """
        credentials_response = self.client.get_credentials_for_identity(
                IdentityId=identity_id,
                Logins={
                    f"cognito-idp.{AWSAddress.REGION.value}.amazonaws.com/{AWSAddress.USER_POOL_ID.value}": idp_token
                },
        )
        return credentials_response
