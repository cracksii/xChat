import requests
from base64 import b64encode
from json import loads, dumps

SERVER = "http://127.0.0.1:5000"
USER, PASSWORD = 1, "cracksii187"

session = requests.session()
token = None


def fetch(url, method, data=None, headers=None):
    headers_dict = {} if headers is None else headers
    headers_dict.update({"Token": token}) if token is not None else None

    if method == "GET":
        if data is not None:
            data = str(data)
            data = data.replace("'", "").replace(": ", "=").replace(",", "&")[1:-1]
        r = session.get(SERVER + url + "?" + data if data is not None else SERVER + url, headers=headers_dict)
    elif method == "POST":
        r = session.post(SERVER + url, headers=headers_dict, data=data)
    elif method == "PUT":
        r = session.put(SERVER + url, headers=headers_dict, data=data)
    elif method == "DELETE":
        r = session.delete(SERVER + url, headers=headers_dict, data=data)
    else:
        raise Exception()

    if not str(r.status_code).startswith("2"):
        raise Exception(r.content.decode("utf-8"))

    return r


# Gets a token
token = fetch("/token", "GET", headers={
    "Authorization": b64encode(f"{USER}:{PASSWORD}".encode("utf-8"))
}).headers["Token"]

# Gets groups
resp = fetch("/groups", "GET")
groups = loads(resp.content.decode())

for group in groups:
    print(f"Group {group}:")

    # Gets all message ids in group
    resp = fetch(f"/messages/{group}", "GET", {
        "timespan": "*"
    })

    m_ids = loads(resp.content.decode())
    for id in m_ids:
        # Gets all messages in group
        print(f"{id}    {loads(fetch(f'/message/{id}', 'GET').content.decode())}")
    print()

resp = fetch("/messages/1", "POST", data={
    "content": '"Nah"'
})
