"""
API Client Module
Handles communication with the server for sending weight data
"""

import requests
from datetime import datetime
from config.settings import API_CONFIG


class APIClient:
    """Handles API communication for sending sensor data"""

    def __init__(self, api_url=None):
        """
        Initialize API client

        Args:
            api_url (str, optional): API endpoint URL. Defaults to config value.
        """
        self.api_url = api_url or API_CONFIG['URL']
        self.timeout = API_CONFIG['TIMEOUT']

    def send_weight_data(self, weight: float):
        """
        Send weight data to server

        Args:
            weight (float): Weight measurement in grams

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure non-negative weight
            safe_weight = 0 if weight < 0 else int(round(weight))
            payload = {"weight": safe_weight}

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[{timestamp}] 📡 Sent: {safe_weight} g | Response: {result}",
                    flush=True
                )
                return True
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"🔗 Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending data: {e}")
            return False

    def test_connection(self):
        """
        Test API connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Send a test payload with weight 0
            response = requests.post(
                self.api_url,
                json={"weight": 0},
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
