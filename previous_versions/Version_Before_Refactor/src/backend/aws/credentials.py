import boto3

app_client_id = '1qgjc5sv6vru4gn2fa197di7hs'
region = 'eu-central-1'
identity_pool_id = 'eu-central-1:832210e8-a0f3-4b19-ab27-f09764c7996a'
user_pool_id = 'eu-central-1_3dVQWMTW0'
aws_account_id = '425229146642'


class Credentials:
    def __init__(self, cognito_idp_response):
        self.region = region

        self.user_pool_id = user_pool_id
        self.aws_account_id = aws_account_id
        self.identity_pool_id = identity_pool_id
        credentials = self.get_credentials(cognito_idp_response=cognito_idp_response)

        if credentials:
            self.aws_access_key_id = credentials['AccessKeyId']
            self.aws_secret_access_key = credentials['SecretKey']
            self.aws_session_token = credentials['SessionToken']

    def get_credentials(self, cognito_idp_response):
        provider_id_token = cognito_idp_response['AuthenticationResult']['IdToken']
        client = boto3.client('cognito-identity', region_name=self.region)

        id_response = client.get_id(
                AccountId=self.aws_account_id,
                IdentityPoolId=self.identity_pool_id,
                Logins={
                    f"cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}": provider_id_token
                }
        )

        credentials_response = client.get_credentials_for_identity(
                IdentityId=id_response['IdentityId'],
                Logins={
                    f"cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}": provider_id_token
                },
                # CustomRoleArn='string'
        )
        return credentials_response['Credentials']
