import unittest
from unittest.mock import patch, mock_open
import os
import json
from cryptography.fernet import Fernet
from datetime import datetime

# Asumiendo las funciones originales
def generate_key():
    if not os.path.exists("key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("key.key", "rb") as key_file:
            key = key_file.read()
    return Fernet(key)

def log_action(action):
    with open("historial.log", "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file)

class TestPasswordManager(unittest.TestCase):

    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_generate_key_creates_key(self, mock_file, mock_exists):
        cipher = generate_key()
        self.assertTrue(isinstance(cipher, Fernet))
        mock_file.assert_called_once_with("key.key", "wb")

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=b"gAAAAABhR0cPIIt9zQJgCm6-YwHFFDKwsEnSPXgQi-UYp2EkA7i5QcQk8X9lPSnG_5izK2Q5dp_A3d9ICF6SsbNLmJshtkwGFQ==")
    def test_generate_key_loads_existing_key(self, mock_file, mock_exists):
        cipher = generate_key()
        self.assertTrue(isinstance(cipher, Fernet))
        mock_file.assert_called_once_with("key.key", "rb")

    @patch("builtins.open", new_callable=mock_open)
    def test_log_action(self, mock_file):
        log_action("Test Action")
        mock_file.assert_called_once_with("historial.log", "a")
        mock_file().write.assert_called_once()
        self.assertIn("Test Action", mock_file().write.call_args[0][0])

    @patch("os.path.exists", return_value=False)
    def test_load_users_no_file(self, mock_exists):
        users = load_users()
        self.assertEqual(users, {})

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='{"user1": "pass1"}')
    def test_load_users_existing_file(self, mock_file, mock_exists):
        users = load_users()
        self.assertEqual(users, {"user1": "pass1"})
        mock_file.assert_called_once_with("users.json", "r")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_users(self, mock_file):
        users = {"user2": "pass2"}
        save_users(users)
        mock_file.assert_called_once_with("users.json", "w")
        written_data = b"".join(call.args[0].encode() for call in mock_file().write.call_args_list)
        self.assertEqual(json.loads(written_data.decode()), users)

if __name__ == "__main__":
    unittest.main()

