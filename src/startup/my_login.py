"""Module for logging"""
import logging
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from tkinter import messagebox, simpledialog, ttk
from typing import Optional, Tuple

import keyring as kr
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from keyring.errors import PasswordDeleteError

from src.backend.AWS.login import CognitoIDPClient, CognitoIDPToken
from src.frontend.screen import IconTypes, Screen
from src.startup.my_configuration import CompleteConfig


class KRUserName(Enum):
    """Keyring usernames. Weird strings used to obfuscate the username"""
    EMAIL = "savlvlkjghljofiajsfoijvaopojojojvhlvhasglbhkljvbhakjvhkjbhckb"
    PASSWORD = "jgjojgoafjblcnbkuhgighaphppoapopoopasughba;lp;oasjvpoabhoap"


class KRServiceName(Enum):
    """Keyring service names. Weird strings used to obfuscate the service"""
    CRED = "flkajlvjkvhaskjhkjhvkjashnjkahaskjfhvas"
    KEY = "jlgnbjkncfjnbjnbjcnbkjcnbkjcnbk"


@dataclass
class LoginDimensionsConfig:
    """Simple settings container for the dimensions of the login screen"""
    button_width: int = 17
    small_button_width: int = 7
    text_entry_width: int = int(1.55 * button_width)
    button_height: int = 1


class LoginScreenUI:
    """Container class for all the UI related elements of the login screen"""

    def __init__(self, login_screen, master: tk.Toplevel, bg_color: CompleteConfig().bg_color):
        cfg = LoginDimensionsConfig()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.auto_login_active = tk.BooleanVar()

        logo_img = Image.open("images/RacingInsights_Icon.png")
        logo_img = logo_img.resize((245, 245))
        logo_photo_img = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(master=master,
                              image=logo_photo_img,
                              bg=bg_color)

        logo_label.image = logo_photo_img

        user_widgets_frame = ttk.Frame(master)
        email_frame = ttk.Frame(user_widgets_frame)
        password_frame = ttk.Frame(user_widgets_frame)
        button_frame = ttk.Frame(user_widgets_frame)

        email_label = ttk.Label(email_frame,
                                text="Email:")

        email_entry = ttk.Entry(email_frame,
                                textvariable=self.email_var,
                                width=cfg.text_entry_width)

        password_label = ttk.Label(password_frame,
                                   text="Password:")

        password_entry = ttk.Entry(password_frame,
                                   textvariable=self.password_var,
                                   show="*",
                                   width=cfg.text_entry_width)

        log_in_btn = ttk.Button(button_frame,
                                text="Log in",
                                command=login_screen.on_log_in,
                                width=cfg.small_button_width)

        signup_btn = ttk.Button(button_frame,
                                text="Sign up",
                                command=login_screen.on_signup,
                                width=cfg.small_button_width)

        forgot_pwd_btn = ttk.Button(user_widgets_frame,
                                    text="Forgot password",
                                    command=login_screen.on_forgot_password,
                                    width=cfg.button_width)

        auto_login_checkbtn = ttk.Checkbutton(user_widgets_frame,
                                              text='Auto-login',
                                              variable=self.auto_login_active,
                                              onvalue=1,
                                              offvalue=0,
                                              command=login_screen.on_activate_auto_login)

        # master.pack(pady=40, padx=0)

        logo_label.pack(pady=40, padx=40)
        user_widgets_frame.pack()

        email_frame.pack(pady=10)
        password_frame.pack(pady=10)
        button_frame.pack(pady=10)
        email_label.pack(pady=5, padx=5, fill='both')
        email_entry.pack(pady=5, padx=5)
        password_label.pack(pady=5, padx=5, fill='both')
        password_entry.pack(pady=5, padx=5)
        log_in_btn.pack(side='left', padx=5)
        signup_btn.pack(side='right', padx=5)
        forgot_pwd_btn.pack(pady=5, padx=5)
        auto_login_checkbtn.pack(pady=10, padx=5)


class LoginScreen(Screen):
    """Screen used when manual login is required"""

    @property
    def icon(self) -> IconTypes:
        return IconTypes.LOGO

    def __init__(self, root: tk.Tk, config: CompleteConfig, cognito: CognitoIDPClient):
        super().__init__(root, title="Login")
        self.cfg_reference = config
        self.cognito = cognito

        self.login_success = False
        self.id_token: Optional[CognitoIDPToken] = None
        self._closed = False

        self.ui = LoginScreenUI(login_screen=self, master=self.screen, bg_color=config.bg_color)

        self.open_in_middle()

        self.screen.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update()

    def on_log_in(self) -> None:
        """Event associated with the login button press"""
        email, password = self.get_inputs()
        login_success, id_token = None, None

        if email and password:
            login_success, id_token = self.cognito.get_login(email=email, password=password)

        self.login_success, self.id_token = login_success, id_token

        if self.login_success:
            if self.ui.auto_login_active.get():
                store_encrypted(username=KRUserName.EMAIL, secret=email)
                store_encrypted(username=KRUserName.PASSWORD, secret=password)

            self.on_close()

    def on_signup(self) -> None:
        """Event associated with the signup button press"""
        email, password = self.get_inputs()

        if email and password:
            self.cognito.sign_up(email=email, password=password)

    def on_forgot_password(self) -> None:
        """Event associated with the forgot password button press"""
        email = self.ui.email_var.get()

        if not email:
            email = simpledialog.askstring("Forgot Password", "Please enter your email address:")
            if not email:
                return

        email, password = self.cognito.forgot_password(email=email)

        self.ui.email_var.set(email)
        self.ui.password_var.set(password)

    def on_activate_auto_login(self):
        """Event associated with the auto login checkbutton press"""
        # Need to remember the desired_state of the auto login button
        self.cfg_reference.auto_login = self.ui.auto_login_active.get()

        self.screen.configure()  # Update visually first to avoid graphical delay

        delete_encrypted()

    def get_inputs(self) -> Tuple[Optional[str], Optional[str]]:
        """Returns the text var inputs if available"""
        email = self.ui.email_var.get()
        password = self.ui.password_var.get()

        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return None, None

        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return None, None

        return email, password

    def on_close(self):
        """Handles all processes on login window close"""
        for element in self.screen.winfo_children():
            element.destroy()

        self.screen.destroy()
        self._closed = True

    def update(self):
        """Update the login screen continuously until it is closed"""
        while True:
            self.screen.configure()

            if self._closed:
                self.screen.destroy()
                break


def do_login(root: tk.Tk, config: CompleteConfig) -> Tuple[bool, Optional[CognitoIDPToken]]:
    """Performs a full login cycle. If auto login fails, manual will be asked"""
    cognito = CognitoIDPClient()

    if config.auto_login:
        login_success, id_token = login_automatically(cognito=cognito)
        if login_success:
            return login_success, id_token

    return login_manually(root, config, cognito=cognito)


def login_automatically(cognito: CognitoIDPClient) -> Tuple[bool, Optional[CognitoIDPToken]]:
    """Attempts automatic login (without UI inputs), returns false if failed"""
    stored_email = retrieve_decrypted(username=KRUserName.EMAIL)
    stored_password = retrieve_decrypted(username=KRUserName.PASSWORD)

    if not (stored_email and stored_password):
        logging.info("Auto-login failed: No login tokens were found on device")
        return False, None

    return cognito.get_login(email=stored_email, password=stored_password)


def login_manually(root: tk.Tk, config: CompleteConfig, cognito: CognitoIDPClient) -> Tuple[
    bool, Optional[CognitoIDPToken]]:
    """Function used for manually logging in to cognito"""
    # Open login screen
    login_screen = LoginScreen(root, config, cognito=cognito)

    return login_screen.login_success, login_screen.id_token


def retrieve_decrypted(username: KRUserName) -> Optional[str]:
    """Retrieves a decrypted token from the vault based on the username"""
    enc_message = kr.get_password(KRServiceName.CRED.value, username.value)
    key = kr.get_password(KRServiceName.KEY.value, username.value)

    if not key:
        return None

    # Instance the Fernet class with the key
    fernet = Fernet(key)
    decrypted_secret = fernet.decrypt(enc_message).decode()
    logging.info("token of type '%s' was found", username)
    return decrypted_secret


def delete_encrypted() -> None:
    """Deletes any encrypted tokens stored in the vault"""
    for element in KRServiceName:
        service = element.value
        for name in KRUserName:
            user = name.value
            try:
                kr.delete_password(service_name=service, username=user)
            except PasswordDeleteError as exception:
                logging.info("token could not be deleted, exception: %s", exception)


def store_encrypted(username: KRUserName, secret: str) -> None:
    """Stores the encrypted tokens in the vault"""
    key = Fernet.generate_key()

    # Instance the Fernet class with the key
    fernet = Fernet(key)

    encrypted_secret = fernet.encrypt(secret.encode())

    kr.set_password(KRServiceName.CRED.value, username.value, str(encrypted_secret, 'utf-8'))
    kr.set_password(KRServiceName.KEY.value, username.value, str(key, 'utf-8'))

    logging.info("token of type '%s' was stored", username.value)
