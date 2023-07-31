import codecs
import logging
import tkinter as tk
from tkinter import Tk, messagebox, simpledialog, ttk

import boto3
import keyring
import keyring.backends.Windows  # Needed for keyring to work
import win32api  # import of these is required as they are dynamically but nuitka doesn't realise
import win32timezone
import yaml
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from keyring.backends import Windows
from keyring.errors import PasswordDeleteError

from previous_versions.Version_Before_Refactor.src.backend.aws.credentials import app_client_id, region
from previous_versions.Version_Before_Refactor.src.frontend.configurations import LoginScreenConfig


class LoginScreen:
    def __init__(self, master: Tk, config_data):
        self.log_id = None
        self.master = master
        self.cognito_idp_response = None  # Needed for getting the (temporary) credentials to AWS resources
        self.cfg = LoginScreenConfig(**config_data['login'])
        self.cfg_data = config_data
        self._closed = False
        self.successful_login = False
        self.cognito = boto3.client('cognito-idp', region_name=region)
        self.master.title("Login")
        self.master.config(width=self.cfg.width, height=self.cfg.height, bg=self.cfg.bg_color)
        self.master.withdraw()

        self.open_in_middle()
        self.master.iconbitmap("images/RacingInsights_Logo.ico")

        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.auto_login_activation = tk.BooleanVar()
        self.tokens_found = False

        logging.info("Time now in UTC: %s", win32timezone.utcnow())  # Only here to trigger import of win32timezone
        logging.info("Local time now: %s", win32api.GetLocalTime())  # Only here to trigger import of win32api

        keyring.set_keyring(Windows.WinVaultKeyring())
        logging.info("Keyring method after setting it: " + str(keyring.get_keyring()))

        self.all_containing_frame = ttk.Frame(self.master)

        logo_img = Image.open("images/RacingInsights_Icon.png")
        logo_img = logo_img.resize((245, 245))
        logo_photo_img = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(master=self.all_containing_frame, image=logo_photo_img, bg=self.cfg.bg_color)
        logo_label.image = logo_photo_img

        self.user_widgets_frame = ttk.Frame(self.all_containing_frame)

        self.email_frame = ttk.Frame(self.user_widgets_frame)
        self.password_frame = ttk.Frame(self.user_widgets_frame)
        self.button_frame = ttk.Frame(self.user_widgets_frame)

        self.email_label = ttk.Label(self.email_frame, text="Email:")
        self.email_entry = ttk.Entry(self.email_frame, textvariable=self.email_var,
                                     width=self.cfg.text_entry_width)

        self.password_label = ttk.Label(self.password_frame, text="Password:")
        self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password_var, show="*",
                                        width=self.cfg.text_entry_width)

        self.log_in_button = ttk.Button(self.button_frame, text="Log in", command=self.on_log_in,
                                        width=self.cfg.small_button_width)
        self.signup_button = ttk.Button(self.button_frame, text="Sign up", command=self.on_signup,
                                        width=self.cfg.small_button_width)

        self.forgot_password_button = ttk.Button(self.user_widgets_frame, text="Forgot password",
                                                 command=self.on_forgot_password,
                                                 width=self.cfg.button_width)
        self.auto_login_checkbutton = ttk.Checkbutton(self.user_widgets_frame, text='Auto-login',
                                                      variable=self.auto_login_activation,
                                                      onvalue=1, offvalue=0, command=self.delete_encrypted)

        self.all_containing_frame.pack(pady=40, padx=0)
        logo_label.pack()
        self.user_widgets_frame.pack()
        self.email_frame.pack(pady=10)
        self.password_frame.pack(pady=10)
        self.button_frame.pack(pady=10)

        self.email_label.pack(pady=5, padx=5, fill='both')
        self.email_entry.pack(pady=5, padx=5)

        self.password_label.pack(pady=5, padx=5, fill='both')
        self.password_entry.pack(pady=5, padx=5)

        self.log_in_button.pack(side='left', padx=5)
        self.signup_button.pack(side='right', padx=5)

        self.forgot_password_button.pack(pady=5, padx=5)
        self.auto_login_checkbutton.pack(pady=10, padx=5)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.on_start()

        self.update()

    def open_in_middle(self):
        # get screen width and height
        screen_width = self.master.winfo_screenwidth()  # width of the screen
        screen_height = self.master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (screen_width / 2) - (self.cfg.width / 2)
        y = (screen_height / 2) - (self.cfg.height / 2)

        # set the dimensions of the screen and where it is placed
        self.master.geometry(f"{self.cfg.width}x{self.cfg.height}+{int(x)}+{int(y)}")

    def update(self):
        """
        Update the login screen in continuously until it is closed
        :return:
        """
        while True:
            self.master.update()

            if self._closed:
                break

    def on_close(self):
        self.save_login_config()

        for element in self.master.winfo_children():
            element.destroy()

        self._closed = True

    def on_start(self):
        self.auto_login_activation.set(self.cfg.auto_login_activation)

        if self.auto_login_activation.get():
            self.login_automatically()
        else:
            self.master.deiconify()

    def login_automatically(self):
        stored_email_token = self.retrieve_decrypted(token_type="email")
        stored_password_token = self.retrieve_decrypted(token_type="password")

        if not (stored_email_token and stored_password_token):
            logging.info("No login credentials were previously stored, could not perform auto-login")
            self.master.deiconify()
            return

        self.tokens_found = True
        self.on_log_in(email=stored_email_token, password=stored_password_token)

    def on_log_in(self, email=None, password=None):
        if not (email and password):  # In case the log_in button is pressed manually
            email = self.email_var.get()
            password = self.password_var.get()

        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return

        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return

        try:
            cognito_idp_response = self.cognito.initiate_auth(
                    ClientId=app_client_id,
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                        'PASSWORD': password
                    }
            )
            _ = cognito_idp_response['AuthenticationResult']['AccessToken']

        except self.cognito.exceptions.NotAuthorizedException as exception:
            logging.info(exception.response)
            if self.tokens_found:
                messagebox.showerror("Error", "The previously stored credentials are outdated.\n"
                                              "Please log in again with your email and password.")
                self.delete_encrypted()
                self.tokens_found = False
                self.master.deiconify()
            else:
                messagebox.showerror("Error", exception.response['message'])
                self.master.deiconify()

        except self.cognito.exceptions.InvalidParameterException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "Invalid parameter(s) entered")
            self.master.deiconify()

        else:
            logging.info("Successful login")
            self.successful_login = True
            self.set_log_id(email=email)
            # In case of auto-login requested for next login and tokens not yet stored
            if self.auto_login_activation.get() and not self.tokens_found:
                # Encrypt and store the email and password tokens safely on the device
                self.store_encrypted(token_type="email", token=email)
                self.store_encrypted(token_type="password", token=password)

            # If a response available, then save this attribute to later use it for credential access to AWS resources
            self.cognito_idp_response = cognito_idp_response
            self.on_close()

    def set_log_id(self, email):
        log_id = codecs.encode(email, 'rot13')  # Used later for logging to database
        log_id = log_id.replace('@', '')
        self.log_id = log_id.replace('.', '_')

    def on_signup(self):
        email = self.email_var.get()
        password = self.password_var.get()

        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return

        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return

        try:
            self.cognito.sign_up(
                    ClientId=app_client_id,
                    Username=f"user_email:{email}",
                    Password=password,
                    UserAttributes=[
                        {
                            'Name': 'email',
                            'Value': f'{email}'
                        }],
            )
            messagebox.showinfo("Success", "Account created successfully, please confirm your email.")

            email_verification_code = simpledialog.askstring("Email Verification",
                                                             "Please enter the verification code sent to your email:")
            self.cognito.confirm_sign_up(
                    ClientId=app_client_id,
                    Username=f"user_email:{email}",
                    ConfirmationCode=email_verification_code
            )
            messagebox.showinfo("Success", "Account created successfully, email verified.")

        except self.cognito.exceptions.UsernameExistsException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "An account with this email already exists.")

        except self.cognito.exceptions.InvalidParameterException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "Invalid parameter(s) entered")

        except self.cognito.exceptions.InvalidPasswordException as exception:
            logging.info(exception.response)
            messagebox.showerror("Error", "The password did not conform with the policy\n\n"
                                          "Password minimum length: 8 characters\n"
                                          "Include a minimum of three of the following mix of character types: "
                                          "Uppercase, Lowercase, Numbers, "
                                          "Non-alphanumeric characters ( ! @ # $ % ^ & * ( ) _ + - = [ ] {} | ' )")

    def on_forgot_password(self):
        email = self.email_var.get()

        if not email:
            email = simpledialog.askstring("Forgot Password", "Please enter your email address:")

        if not email:
            return

        _ = self.cognito.forgot_password(ClientId=app_client_id, Username=f"user_email:{email}")

        messagebox.showinfo("Success", "Use the verification code sent to the email to restore your password.\n"
                                       "If you did not receive any email, please use the 'Sign Up' button instead.")

        email_verification_code = simpledialog.askstring("Email Verification",
                                                         "Please enter the verification code sent to your email:")

        if email_verification_code:
            new_password = simpledialog.askstring("Create New Password", "Please enter a new password:", show="*")

            self.cognito.confirm_forgot_password(ClientId=app_client_id,
                                                 Username=f"user_email:{email}",
                                                 ConfirmationCode=email_verification_code,
                                                 Password=new_password)

            messagebox.showinfo("Success", "Password updated successfully.")

            # Pre-fill the variables in the login page as they have already been entered and confirmed by the user
            self.email_var.set(email)
            self.password_var.set(new_password)

    def save_login_config(self):
        config_dict = self.cfg_data
        config_dict["login"]["auto_login_activation"] = self.auto_login_activation.get()
        with open(r'config_data.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(config_dict, file)

    def delete_encrypted(self):
        self.master.update()  # To avoid visual delay of seeing the checkbox change
        tokens = ["email", "password"]

        for token in tokens:
            try:
                keyring.delete_password("RacingInsights-App", f"{token}_key")
                logging.info("deleted the encrypted key stored for %s", token)
            except PasswordDeleteError as exception:
                logging.info("token could not be deleted, exception: %s", exception)

    @staticmethod
    def store_encrypted(token_type, token):
        key = Fernet.generate_key()

        # Instance the Fernet class with the key
        fernet = Fernet(key)

        encrypted_token = fernet.encrypt(token.encode())

        keyring.set_password("RacingInsights-App", token_type, str(encrypted_token, 'utf-8'))
        keyring.set_password("RacingInsights-App", f"{token_type}_key", str(key, 'utf-8'))

        logging.info("token of type '%s' was stored", token_type)

    @staticmethod
    def retrieve_decrypted(token_type):
        enc_message = keyring.get_password("RacingInsights-App", token_type)

        # key = Fernet.generate_key()
        key = keyring.get_password("RacingInsights-App", f"{token_type}_key")

        if not key:
            return None

        if key:
            # Instance the Fernet class with the key
            fernet = Fernet(key)

            decrypted_token = fernet.decrypt(enc_message).decode()

            logging.info("token of type '%s' was found", token_type)
            return decrypted_token
