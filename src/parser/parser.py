import os, zulip, requests
from urllib.parse import urljoin

from src.model.model import recognize
client = zulip.Client(config_file="~/test/test/src/parser/zuliprc")
resp = client.get_users(request={"client_gravatar": True})
users = resp['members']

for user in users:
    uid = user["user_id"]
    uemail = user["email"]
    if user["avatar_url"] == None and user["is_bot"] == False:
        with open("data/no_avatars.txt", "a+") as f:
            f.write(f"{uemail}\n")
    else:
        url = urljoin(f"{client.base_url}/", user.get("avatar_url"))
        with open("data/avatars.txt", "a+") as f:
            f.write(f"{url} {uemail}\n")
