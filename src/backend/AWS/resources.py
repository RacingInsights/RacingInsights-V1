import logging
from enum import Enum
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from dynamodb_json import json_util

from src.backend.AWS.addresses import AWSAddress
from src.backend.AWS.credentials import AWSCredentials


class TableNames(Enum):
    """The different dynamoDB table names"""
    RELATIVE = "Relative_Estimation_Data"


class AWSResources:
    """Container for all the various AWS resources/clients"""

    def __init__(self, aws_credentials: AWSCredentials):
        self.dynamo_db = DynamoDB(aws_credentials=aws_credentials)
        # self.s3 = S3(aws_credentials=aws_credentials)


class DynamoDB:
    """General DynamoDB connection(s)"""

    def __init__(self, aws_credentials: AWSCredentials):
        self.resource = boto3.resource('dynamodb',
                                       aws_access_key_id=aws_credentials.access_key_id,
                                       aws_secret_access_key=aws_credentials.secret_access_key,
                                       aws_session_token=aws_credentials.session_token,
                                       region_name=AWSAddress.REGION.value
                                       )


class DynamoDBTable:
    """Class for instantiating and interacting with specific tables in the DynamoDB resource"""

    def __init__(self, dynamo_db: DynamoDB, name: TableNames):
        self.table = dynamo_db.resource.Table(name)

    def get_item(self, key: dict, projection_expression: str, expression_attr_name: dict) -> Optional[dict]:
        """
        Gets the item from the given table
        Example inputs:
            key = {'track_id': 69},
            projection_expression = "EstimationData.#key_name,TrackVersion",
            expression_attr_name = {'#key_name': str(4011)}

        Example item:
        {
            'EstimationData':
                {
                    "4011":
                    {
                        "DistancePct": [],
                        "EstimateTime": [],
                        "ResolutionPct": 0.0024154589371980675
                    }
                }
            'TrackVersion': "2022.11.22.02",
        }
        """
        table_response = self._get_table_response(key, projection_expression, expression_attr_name)
        item = self._get_item_from_response(table_response=table_response)
        return item

    def _get_table_response(self, key: dict, projection_expression: str, expression_attr_name: dict) -> Optional[dict]:
        """Returns the response from the table when trying to get a specific item"""
        try:
            table_response = self.table.get_item(  # EXAMPLE:
                    Key=key,  # {'track_id': track_id},
                    ProjectionExpression=projection_expression,  # "EstimationData.#key_name,TrackVersion",
                    ExpressionAttributeNames=expression_attr_name  # {'#key_name': str(car_class)}
            )
        except ClientError as exc:
            logging.error("%s:%s", exc.response['Error']['Code'], exc.response['Error']['Message'])
            return None
        return table_response

    @staticmethod
    def _get_item_from_response(table_response) -> Optional[dict]:
        """Returns the item from the table response if it is available"""
        if not table_response:
            return None

        try:
            item = table_response['Item']
        except KeyError as exc:
            logging.warning("No %s-key in the response from the db", exc)
            return None
        return json_util.loads(item)

    def update_item(self, key: Tuple, update_expression, expression_attr_names, expression_attr_values):
        """Simple wrapper of boto method to make it clear how updating is done for a table"""
        self.table.update_item(
                Key={key[0]: key[1]},  # {'track_id': track_id},
                UpdateExpression=update_expression,  # 'SET EstimationData.#new_key = :new_value',
                ExpressionAttributeNames=expression_attr_names,  # {'#new_key': car_class_key},
                ExpressionAttributeValues=expression_attr_values  # {':new_value': car_class_estimation_data}
        )
