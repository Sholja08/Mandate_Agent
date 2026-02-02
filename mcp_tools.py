import json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "upi_mandates.json")


def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------------- MCP TOOLS ----------------
def get_all_mandates():
    data = load_data()
    return {
        "mandates": [
            {
                "mandate_id": m["mandate_id"],
                "mandate_name": m["mandate_name"],
                "status": m["status"]
            }
            for m in data
        ]
    }


def get_mandate_details(query: str):
    query = query.lower()

    matches = [
        m for m in load_data()
        if query in m["mandate_name"].lower()
        or query in m["mandate_id"].lower()
        or query in m["phone_no"]
    ]

    if not matches:
        return {"matches": []}

    return {"matches": matches}



def pause_mandate(query: str):
    data = load_data()
    found = []

    for m in data:
        if query.lower() in json.dumps(m).lower():
            m["status"] = "pause"
            found.append(m)

    save_data(data)
    return {"success": bool(found), "updated": found}


def unpause_mandate(query: str):
    data = load_data()
    found = []

    for m in data:
        if query.lower() in json.dumps(m).lower():
            m["status"] = "unpaused"
            found.append(m)

    save_data(data)
    return {"success": bool(found), "updated": found}


def revoke_mandate(query: str):
    data = load_data()
    remaining, revoked = [], []

    for m in data:
        if query.lower() in json.dumps(m).lower():
            revoked.append(m)
        else:
            remaining.append(m)

    save_data(remaining)
    return {"revoked": revoked, "remaining": len(remaining)}
