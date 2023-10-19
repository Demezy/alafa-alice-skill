from postgrest.exceptions import APIError
from config import URL, KEY
from supabase import create_client, Client
from fastapi import FastAPI, Request
import datetime
from random import randint

supabase: Client = create_client(URL, KEY)

alice_code_start_range = 1000
alice_code_end_range = alice_code_start_range * 10


app = FastAPI()


issue_date = datetime.datetime
user_id = str
login_record = tuple[issue_date, user_id]
pincode = str
alice_login: dict[pincode, login_record] = {}


@app.post("/select_user_id")
def select_user_id(data: dict):
    aliceId = data["alice_id"]
    alice = (
        supabase.table("alice").select("user_id").eq("alice_id", aliceId).execute().data
    )
    print(alice)
    if len(alice) == 0:
        return {"error": "unkwnown alice"}
    return {"user_id": alice[0]["user_id"]}


@app.post("/balances")
def get_balances(data: dict):
    userId = data["user_id"]
    # balances = maybe_select("accounts", "*", "user_id", userId)
    try:
        balances = (
            supabase.table("accounts").select("*").eq("user_id", userId).execute()
        )
        if len(balances.data) == 0:
            return {"error": "i dont know, probably user id invalid"}
    except:
        return {"error": "i dont know, probably user id invalid"}

    return balances


@app.post("/pair_alice")
def pair_alice(data: dict):
    aliceId = data["alice_id"]
    code: pincode = data["code"]
    record = alice_login.pop(code, None)
    if record is None:
        return {"success": False, "purpose": "ivalid code"}

    timestamp, userId = record
    if (datetime.datetime.now() - timestamp).seconds > 180:
        return {"success": False, "purpose": "code is dead, you are next"}

    add_alice_user_pair(aliceId, userId)
    return {"success": True, "user_id": userId}


@app.get("/backdoor/redis")
def backdoor_redis():
    return alice_login


@app.post("alice/state")
def get_alice_state(data: dict):
    alice_id = data["alice_id"]


@app.post("/init_pair_alice")
def init_pair_alice(data: dict):
    userId = data["user_id"]
    userTable = maybe_select("users", "id", "id", userId)

    if userTable == None:
        return {"error": "invalid user id"}

    code = str(randint(a=alice_code_start_range, b=alice_code_end_range))
    alice_login[code] = (
        issue_date.now(),
        userId,
    )
    return {"code": code}


def maybe_select(table_name, select, field_name, equal_to):
    try:
        singular = (
            supabase.table(table_name).select(select).eq(field_name, equal_to).execute()
        )
        if len(singular.data) != 1:
            return None
        return singular.data[0]
    except APIError:
        return None


def add_alice_user_pair(aliceId, userId):
    supabase.table("alice").delete().eq("alice_id", aliceId).execute()
    return (
        supabase.table("alice")
        .insert({"user_id": userId, "alice_id": aliceId})
        .execute()
    )


if __name__ == "__main__":
    # print(get_balances("56f5788d-fe5f-4634-bcec-6dffd5968afb"))
    # print(get_balances("2aa0923b-03e8-47ed-9bb5-5b740915f551"))
    # print(
    #     add_alice_user_pair(
    #         aliceId="alice test", userId="56f5788d-fe5f-4634-bcec-6dffd5968afb"
    #     )
    # )
    # print(maybe_select("users", "id", "56f5788d-fe5f-4634-bcec-6dffd5968afb"))
    # print(add_alice_user_pair("alice testdsad", "56f5788d-fe5f-4634-bcec-6dffd5968afb"))
    # print( select_user_id( { "alice_id": "267AC06107A47A6766D77A564AC4CF24DD1BBF42BBF9BA0EC77A5190BF804BAA" }))
    pass

    import requests as req

    SERVER_URL = "http://51.250.28.5:8000/"
    r = req.post(SERVER_URL + "pair_alice", json={"alice_id": "asd", "code": "123"})
    print(r.text)
