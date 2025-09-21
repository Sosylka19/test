import zulip
from urllib.parse import urljoin
from time import strftime, localtime

client = zulip.Client(config_file="~/test/test/src/parser/zuliprc")
resp = client.get_users(request={"client_gravatar": True})
users = resp['members']
last_time_active = client.get_realm_presence()
end_info = list(zip(users, last_time_active['presences'].values()))

for user in end_info:
    uid = user[0]['user_id']
    uemail = user[0]['email']
    last_time_active = strftime('%Y-%m-%d %H:%M:%S', localtime(user[1].get('aggregated', 0).get('timestamp', 0)))
    if user[0]["avatar_url"] == None and user[0]["is_bot"] == False:
        with open("data/no_avatars.txt", "a+") as f:
            f.write(f"{uemail} {last_time_active}\n")
    else:
        if user[0]["is_bot"] == True:
            continue
        url = urljoin(f"{client.base_url}/", user[0].get("avatar_url"))
        with open("data/avatars.txt", "a+") as f:
            f.write(f"{url} {uemail} {last_time_active}\n")
