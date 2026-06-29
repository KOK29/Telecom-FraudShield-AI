ALL_COMPONENTS = [
    "OUTGOING_CALLS",
    "INTERNATIONAL_CALLS",
    "SMS_SERVICE",
    "DATA_SERVICE",
    "SIM_OPERATIONS",
    "ROAMING",
]

COMPONENT_STATUS = {comp: "ACTIVE" for comp in ALL_COMPONENTS}
SIM_STATUS = {}


def block_component(name):
    if name in COMPONENT_STATUS:
        COMPONENT_STATUS[name] = "BLOCKED"


def unblock_component(name):
    if name in COMPONENT_STATUS:
        COMPONENT_STATUS[name] = "ACTIVE"


def shutdown_component(name):
    if name in COMPONENT_STATUS:
        COMPONENT_STATUS[name] = "SHUTDOWN"


def is_blocked(name):
    return COMPONENT_STATUS.get(name) in ("BLOCKED", "SHUTDOWN")


def get_component_status():
    return dict(COMPONENT_STATUS)


def reset_all_components():
    for comp in ALL_COMPONENTS:
        COMPONENT_STATUS[comp] = "ACTIVE"


def protection_action(probability, input_data):
    actions = []
    if probability >= 0.80:
        actions += [
            "BLOCK_OUTGOING_CALLS", "BLOCK_INTERNATIONAL_CALLS", "BLOCK_SMS_SERVICE",
            "LOCK_SIM_OPERATIONS", "REQUIRE_CUSTOMER_VERIFICATION", "ESCALATE_TO_FRAUD_TEAM"
        ]
    elif probability >= 0.60:
        actions += ["BLOCK_INTERNATIONAL_CALLS", "LIMIT_DAILY_CALLS", "REQUIRE_CUSTOMER_VERIFICATION"]
    elif probability >= 0.35:
        actions += ["ENABLE_ENHANCED_MONITORING", "SEND_WARNING_TO_CUSTOMER"]
    elif probability >= 0.15:
        actions.append("PASSIVE_MONITORING")
    else:
        actions.append("NO_ACTION")

    if input_data.get("sim_changes", 0) >= 5:
        actions.append("LOCK_SIM_SWAP_REQUEST")
    if input_data.get("international_calls", 0) > 300:
        actions.append("TEMP_BLOCK_ROAMING")
    if input_data.get("sms_per_day", 0) > 1000:
        actions.append("TEMP_BLOCK_SMS")
    return list(dict.fromkeys(actions))


def ban_sim(sim_id):
    SIM_STATUS[sim_id] = "BANNED"


def unban_sim(sim_id):
    SIM_STATUS[sim_id] = "ACTIVE"


def deactivate_sim(sim_id):
    SIM_STATUS[sim_id] = "DEACTIVATED"


def is_sim_banned(sim_id):
    return SIM_STATUS.get(sim_id) in ("BANNED", "DEACTIVATED")


def get_sim_status(sim_id):
    return SIM_STATUS.get(sim_id, "ACTIVE")


def get_all_sim_statuses():
    return dict(SIM_STATUS)
