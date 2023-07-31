import decimal
import json
import logging

import boto3
from botocore.exceptions import ClientError
from dynamodb_json import json_util

from previous_versions.Version_Before_Refactor.src.backend.aws.credentials import Credentials

print(decimal.Decimal('1.2'))  # Just to trigger it


class RelativeEstimationDataDBLink:
    """Encapsulates the Amazon DynamoDB table of Relative_Estimation_Data."""

    def __init__(self):
        self.dynamo_db_resource = None
        self.table = None
        self.name = "Relative_Estimation_Data"
        logging.info("Initialized a RelativeEstimationDataDBLink instance")

    def set_resource(self, credentials: Credentials):
        self.dynamo_db_resource = boto3.resource('dynamodb',
                                                 aws_access_key_id=credentials.aws_access_key_id,
                                                 aws_secret_access_key=credentials.aws_secret_access_key,
                                                 aws_session_token=credentials.aws_session_token,
                                                 region_name=credentials.region
                                                 )

        self.table = self.dynamo_db_resource.Table(self.name)

    def get_relative_estimation_data(self, track_id: int, car_class: int) -> dict | None:
        """
        Gets the relative estimation data from the dynamo db table for the specific track_id and car class
        :param car_class:
        :param track_id:
        :return: relative_estimation_data_db_link | None

        example: relative_estimation_data_db_link =
        {
            'EstimationData':
                {
                    "4011":
                    {
                        "DistancePct": [],
                        "EstimateTime": [],
                        "CurrentReferencePctStored": []
                        "ResolutionPct": 0.0024154589371980675
                    }
                }
            'TrackVersion': "2022.11.22.02",
        }
        """
        if not (self.dynamo_db_resource and self.table):
            logging.exception("Couldn't 'get_relative_estimation_data' because resource is not available.")
            return None

        try:
            response = self.table.get_item(
                    Key={'track_id': track_id},
                    ProjectionExpression="EstimationData.#key_name,TrackVersion",
                    ExpressionAttributeNames={'#key_name': str(car_class)}
            )
        except ClientError as e:
            logging.error(f"Couldn't get the track with track_id={track_id} from {self.table.name}.\n"
                          f"Here's why: {e.response['Error']['Code']}"
                          f": {e.response['Error']['Message']}")
            return None
        else:
            try:
                item = response['Item']
            except KeyError as e:
                logging.warning(f"No {e}-key in the response from the db when requesting the data for "
                                f"track_id={track_id}")
                return None
            else:
                relative_estimation_data = json_util.loads(item)
                return relative_estimation_data

    def send_relative_estimation_data(self, track_id: int, data):
        """
        :param track_id:
        :param data:
        Example of 'data':
        data = \
        {
            "TrackDisplayName": Mount Panorama Circuit
            "TrackLengthOfficial": "6.21 km",
            "TrackConfigName": null,
            "TrackVersion": "2022.11.22.02",
            "EstimationData": \
            {
                "4011": \
                {
                    "DistancePct": [],
                    "EstimateTime": [],
                    "CurrentReferencePctStored": []
                    "ResolutionPct": 0.0024154589371980675
                }
            }
        }
        :return:
        """
        car_class_key = list(data["EstimationData"].keys())[0]
        car_class_estimation_data = list(data['EstimationData'].values())[0]

        estimation_data_dynamo_db = json.loads(json.dumps(car_class_estimation_data), parse_float=decimal.Decimal)

        # Check current version stored in db
        version_in_db = self.get_track_version_in_db(track_id=track_id)

        try:
            if version_in_db == data['TrackVersion']:
                self.append_class_to_item(track_id=track_id,
                                          car_class_key=car_class_key,
                                          car_class_estimation_data=estimation_data_dynamo_db)

            else:  # The current version of track stored in db is outdated, overwrite it with new version
                self.make_new_track_item(complete_data=data, track_id=track_id)
                logging.info(f"Made new track item in db for track_id={track_id}")

        except Exception as e:  # The item (track) might not yet be available, then make a new one instead
            logging.warning("Error occurred when initially trying to send relative data to the database.\n"
                            "%s\n"
                            "Will attempt to create a new (or overwritten) item instead", e)
            self.make_new_track_item(complete_data=data, track_id=track_id)
            logging.info(f"Made new track item in db for track_id={track_id}")

    def make_new_track_item(self, complete_data: dict, track_id: int):
        # Convert to dynamodb format and add track_id to the dict
        dynamodb_item = json.loads(json.dumps(complete_data), parse_float=decimal.Decimal)
        dynamodb_item['track_id'] = track_id

        try:
            self.table.put_item(Item=dynamodb_item)

        except Exception as e:
            logging.error(f"Couldn't put the track with track_id={track_id} to {self.table.name}.\n"
                          f"Here's why: {e}")

    def append_class_to_item(self, track_id: int, car_class_key: str, car_class_estimation_data):
        self.table.update_item(
                Key={'track_id': track_id},
                UpdateExpression='SET EstimationData.#new_key = :new_value',
                ExpressionAttributeNames={'#new_key': car_class_key},
                ExpressionAttributeValues={':new_value': car_class_estimation_data}
        )

    def get_track_version_in_db(self, track_id: int):
        try:
            response = self.table.get_item(
                    Key={'track_id': track_id},
                    ProjectionExpression="TrackVersion",
            )
        except Exception as e:
            logging.exception(e)
        else:
            try:
                track_version = response['Item']['TrackVersion']
            except KeyError:
                logging.warning("Track was not available in db when check for the track version")
            else:
                return track_version
