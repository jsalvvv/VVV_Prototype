import requests
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def get_request(url: str, params: dict = None) -> dict:
    """
    Makes a request to the API and returns the response in JSON format. When passing any params, we force the format to be JSON.
    
    Params:
        url (str): The URL to make the request to.
        params (dict, optional): The parameters to pass to the request. Defaults to None.
    
    Returns:
        dict: The response in JSON format.
    """
    headers = {
        "Accept": "application/json"
    }
    auth = (
        os.environ.get("USERNAME"),
        os.environ.get("PASSWORD"),
    )
    
    response = requests.get(
        url, 
        params=params, 
        auth=auth,
        headers=headers
    )
    response.raise_for_status()
    return response.json()