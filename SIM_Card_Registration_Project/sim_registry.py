import pandas as pd
from datetime import datetime
from supabase_client import get_supabase

SIM_CUSTOMER_COLUMNS = [
    "sim_id", "full_name", "nrc", "location", "phone_number",
    "email", "status", "registered_at"
]


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def register_sim_customer(sim_id, full_name, nrc, location, phone_number="", email="", status="ACTIVE"):
    record = {
        "sim_id": sim_id.strip(),
        "full_name": full_name.strip(),
        "nrc": nrc.strip(),
        "location": location.strip(),
        "phone_number": phone_number.strip(),
        "email": email.strip().lower(),
        "status": status.strip().upper() if status else "ACTIVE",
        "registered_at": _now(),
    }

    get_supabase().table("sim_customers").upsert(record, on_conflict="sim_id").execute()
    return record


def get_all_sim_customers():
    data = get_supabase().table("sim_customers").select("*").order("registered_at", desc=True).execute().data
    return pd.DataFrame(data, columns=SIM_CUSTOMER_COLUMNS)


def get_sim_customer(sim_id):
    data = get_supabase().table("sim_customers").select("*").eq("sim_id", sim_id.strip()).limit(1).execute().data
    return data[0] if data else None


def search_sim_customer(keyword):
    df = get_all_sim_customers()
    if df.empty or not keyword:
        return df

    keyword = keyword.lower().strip()
    searchable = ["sim_id", "full_name", "nrc", "location", "phone_number", "email", "status"]
    mask = False
    for col in searchable:
        if col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(keyword, na=False)
    return df[mask]


def delete_sim_customer(sim_id):
    result = get_supabase().table("sim_customers").delete().eq("sim_id", sim_id).execute().data
    return bool(result)
