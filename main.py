"""Module for logging"""
import logging
import time
import tkinter

# import of these is required as they are dynamically but nuitka doesn't realise
import win32api
import win32timezone
import yaml

from src.backend.AWS.credentials import CognitoIdentityClient
from src.backend.AWS.resources import AWSResources
from src.backend.iRacing.telemetry import RITelemetry
from src.client_app.client_app import ClientApp
from src.frontend.user_interface import UserInterface
from src.startup.my_configuration import load_configuration, object_to_dict
from src.startup.my_logger import initialize_logging
from src.startup.my_login import do_login
from src.startup.my_theme import set_my_theme


def main() -> None:
    start = time.time()
    """Main application function"""
    # -- Startup
    initialize_logging(production=False)

    # Only here to trigger imports of win32 libs
    logging.info("Time now in UTC: %s", win32timezone.utcnow())
    logging.info("Local time now: %s", win32api.GetLocalTime())

    # Initialize the configuration - this is used for the app state
    configuration = load_configuration()

    # Initialize tkinter and set the app UI theme
    root = tkinter.Tk()
    root.withdraw()  # Such that it doesn't show the root window
    font = f"{configuration.font.style} {configuration.font.size} {configuration.font.extra}"
    set_my_theme(font=font)

    # Authentication
    login_success, idp_token = do_login(root=root, config=configuration)  # Takes approx 2.8s

    if not login_success:
        logging.info("Login screen was closed without a login, app is closed")
        return

    # -- Backend
    # AWS - User has been authenticated at this point
    cognito_identity_client = CognitoIdentityClient()  # Takes approx 2s
    aws_credentials = cognito_identity_client.get_aws_credentials(idp_token=idp_token)
    aws_resources = AWSResources(aws_credentials=aws_credentials)

    # iRacing
    # Only interaction with this is reading of attributes and calling update()
    ri_telemetry = RITelemetry(dynamo_db_resource=aws_resources.dynamo_db)

    # --Frontend
    user_interface = UserInterface(root, configuration, ri_telemetry)

    # --Client app
    client_app = ClientApp(root, ri_telemetry, user_interface, configuration)
    end = time.time()
    print(end-start)
    client_app.run()

    # Save the final configuration desired_state
    with open(r'config.yaml', 'w', encoding='utf-8') as file:
        _ = yaml.dump(object_to_dict(configuration), file)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception(e)
