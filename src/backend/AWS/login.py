import logging
from dataclasses import dataclass
from tkinter import messagebox, simpledialog
from typing import Optional, Protocol, Tuple

import boto3

from src.backend.AWS.addresses import AWSAddress


@dataclass
class CognitoIDPToken(Protocol):
    """To support type hinting the cognito idp token"""


class CognitoIDPClient:
    """Class for interacting with a cognito identity provider"""

    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=AWSAddress.REGION.value)

    def get_login(self, email: str, password: str) -> Tuple[bool, Optional[CognitoIDPToken]]:
        """Attempts to get an id token from cognito. False and None if failed"""

        login_success, id_token = False, None
        try:
            response = self.client.initiate_auth(
                    ClientId=AWSAddress.APP_CLIENT_ID.value,
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={'USERNAME': email, 'PASSWORD': password}
            )
        except self.client.exceptions.NotAuthorizedException as exception:
            logging.exception(exception.response)
            messagebox.showerror("Error", exception.response['message'])

        except self.client.exceptions.InvalidParameterException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "Invalid parameter(s) entered")

        else:
            login_success = True
            id_token: Optional[CognitoIDPToken] = response['AuthenticationResult']['IdToken']

        return login_success, id_token

    def sign_up(self, email: str, password: str) -> None:
        """Attempts a signup with cognito, displays messageboxes for outcome"""
        try:
            self.client.sign_up(
                    ClientId=AWSAddress.APP_CLIENT_ID.value,
                    Username=email,
                    Password=password,
                    UserAttributes=[
                        {
                            'Name': 'email',
                            'Value': email
                        }],
            )
            messagebox.showinfo("Success", "Account created successfully, please confirm your email.")

            email_verification_code = simpledialog.askstring("Email Verification",
                                                             "Please enter the verification code sent to your email:")

            self.client.confirm_sign_up(
                    ClientId=AWSAddress.APP_CLIENT_ID.value,
                    Username=email,
                    ConfirmationCode=email_verification_code
            )
            messagebox.showinfo("Success", "Account created successfully, email verified.")

        except self.client.exceptions.UsernameExistsException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "An account with this email already exists.")

        except self.client.exceptions.InvalidParameterException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "Invalid parameter(s) entered")

        except self.client.exceptions.InvalidPasswordException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error",
                                 "The password did not conform with the policy\n\n"
                                 "Password minimum length: 8 characters\n"
                                 "Include a minimum of three of the following mix of character types:"
                                 "Uppercase, Lowercase, Numbers, Non-alphanumeric characters ( ! @ # $ % ^ & "
                                 "* () _ + - = [ ] {} | ' )")

    def forgot_password(self, email: str) -> Optional[Tuple[str, str]]:
        """Process used when a password needs to be reset with cognito"""
        _ = self.client.forgot_password(ClientId=AWSAddress.APP_CLIENT_ID.value, Username=email)

        messagebox.showinfo("Success", "Use the verification code sent to the email to restore your password.\n"
                                       "If you did not receive any email, please use the 'Sign Up' button instead.")

        email_code = simpledialog.askstring("Email Verification",
                                            "Please enter the verification code"
                                            "sent to your email:")
        if email_code:
            new_password = simpledialog.askstring("Create New Password", "Please enter a new password:", show="*")

            self.client.confirm_forgot_password(ClientId=AWSAddress.APP_CLIENT_ID.value,
                                                Username=email,
                                                ConfirmationCode=email_code,
                                                Password=new_password)

            messagebox.showinfo("Success", "Password updated successfully.")
            return email, new_password
        return None
