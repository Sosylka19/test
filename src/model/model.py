from PIL import Image
import requests
from io import BytesIO

def recognize():
    with open("data/avatars.txt", "r") as f:
        emails = f.readlines()
        #first - url, second - email
        emails = [email[:-1].split() for email in emails]
        print(emails)

recognize()