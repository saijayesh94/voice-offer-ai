import os

import requests

# from config_Exclusive_Buyer_Tenant_Representation_Agreement import pdf_fields


class MLS:
    """
    A class to interact with MLS for property details.
    """

    def __init__(self):
        # RealtyFeed MLS credentials, read from pdf_filler/.env (see .env.example)
        self.client_id = os.getenv("MLS_CLIENT_ID")
        self.client_secret = os.getenv("MLS_CLIENT_SECRET")
        self.api_key = os.getenv("MLS_API_KEY")
        self.access_token = None

        self.listing_id = None
        self.listing_key = None

    def get_access_token(self):
        """
        Function to get access token from the MLS API using client credentials.

        Returns:
        - str: The access token.
        """
        url = "https://realtyfeed-sso.auth.us-east-1.amazoncognito.com/oauth2/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
        }

        print("Getting access token from MLS API")
        response = requests.post(url, data=data, headers=headers)
        self.access_token = response.json()["access_token"]

    def get_property_details(self):
        """
        Function to get property details from the MLS API using the ListingId.

        Returns:
        - dict: The JSON response containing the property details.
        """

        if not self.listing_id:
            print("ListingId is not provided or is None")
            return None

        url = "https://api.realtyfeed.com/reso/odata/Property"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "x-api-key": self.api_key,
        }

        params = {
            "$filter": f"ListingId eq '{self.listing_id}'",
        }

        print("Getting property details from MLS API")
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("value"):
                self.listing_key = data["value"][0].get(
                    "ListingKey"
                )  # Setting listing Key
                return data
            else:
                print("No property details found for the given ListingId.")
                return None
        else:
            print(
                f"Failed to fetch property details: {response.status_code}, {response.text}"
            )
            return None

        # self.listing_key = response.json()['value'][0]['ListingKey']   # Setting listing Key

    def get_property_by_listing_key(self):
        """
        Function to get property details from the MLS API using the ListingKey.

        Returns:
        - dict: The JSON response containing the property details.
        """
        url = f"https://api.realtyfeed.com/reso/odata/Property/{self.listing_key}"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "x-api-key": self.api_key,
        }

        print(
            f"Getting property details from MLS API for Listing Key: {self.listing_key}"
        )
        response = requests.get(url, headers=headers)
        return response.json()

    def fetch_property_details(self, config_data):
        """
        Fetches property details from the MLS by obtaining an access token, getting property details,
        and retrieving the property by its listing key.

        Returns:
        - dict: property details from the MLS API
        """
        self.listing_id = config_data["property_details"]["listing_id"]

        self.get_access_token()
        self.get_property_details()
        mls_api_res = self.get_property_by_listing_key()
        # print("fdjk", mls_api_res)

        try:
            if mls_api_res["ListingKey"]:
                return mls_api_res
        except Exception:
            return None
