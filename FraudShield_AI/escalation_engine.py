from datetime import timedelta
from sim_registry import (
    register_sim, record_offense, set_ban, update_risk_score,
    check_ban_expired, log_notification, get_sim_record,
)

PENALTY_LEVELS = {
    1: {
        "label": "⚠️ Level 1 — Warning",
        "ban_duration_text": "24 hours",
        "ban_duration": timedelta(hours=24),
        "notification_type": "WARNING",
        "notification_message": "Your SIM card has been temporarily suspended for 24 hours due to suspicious activity. If you believe this is an error, you may file an appeal through the FraudShield dashboard.",
    },
    2: {
        "label": "🚫 Level 2 — Final Warning",
        "ban_duration_text": "7 days",
        "ban_duration": timedelta(days=7),
        "notification_type": "FINAL_WARNING",
        "notification_message": "Your SIM card has been suspended for 7 days following a second violation. This is your FINAL WARNING. Any further violations will result in permanent deactivation.",
    },
    3: {
        "label": "🔴 Level 3 — Permanent Deactivation",
        "ban_duration_text": "Permanent",
        "ban_duration": None,
        "notification_type": "PERMANENT_BAN",
        "notification_message": "Your SIM card has been PERMANENTLY DEACTIVATED due to repeated suspicious activity. Contact your carrier for further information.",
    },
}


def probability_to_severity(probability):
    if probability >= 0.80:
        return "CRITICAL"
    if probability >= 0.60:
        return "HIGH"
    if probability >= 0.35:
        return "MEDIUM"
    return "LOW"


def calculate_risk_score(input_data, probability, offense_count):
    ml_component = probability * 35.0
    rule_score = 0.0
    calls = input_data.get("calls_per_day", 0)
    unique = input_data.get("unique_numbers_called", 0)
    intl = input_data.get("international_calls", 0)
    sms = input_data.get("sms_per_day", 0)
    sim = input_data.get("sim_changes", 0)
    device = input_data.get("device_changes", 0)
    duration = input_data.get("avg_call_duration", 5.0)
    account_age = input_data.get("account_age_days", 500)
    complaints = input_data.get("complaints_count", 0)

    if calls > 300: rule_score += 4
    if calls > 500: rule_score += 5
    if calls > 700: rule_score += 6
    if unique > 150: rule_score += 4
    if unique > 300: rule_score += 5
    if intl > 100: rule_score += 4
    if intl > 250: rule_score += 5
    if sms > 500: rule_score += 3
    if sms > 1000: rule_score += 5
    if sim >= 3: rule_score += 4
    if device >= 3: rule_score += 3
    if sim >= 3 and device >= 3: rule_score += 5
    if complaints >= 5: rule_score += 4
    if duration < 1.0 and calls > 500: rule_score += 5
    if account_age < 90: rule_score += 4

    rule_component = min(rule_score, 40.0)
    offense_component = min(offense_count * 10, 25)
    total = ml_component + rule_component + offense_component
    return int(max(0, min(100, round(total))))


def escalate(sim_id, case_id, probability, input_data):
    register_sim(sim_id)
    ban_expired = check_ban_expired(sim_id)
    current_record = get_sim_record(sim_id)
    was_already_banned = not ban_expired

    if current_record and current_record.get("is_permanently_blocked") in (True, "True", "true", 1, "1"):
        risk_score = calculate_risk_score(input_data, probability, int(current_record.get("offense_count", 3)))
        update_risk_score(sim_id, risk_score)
        return {
            "sim_id": sim_id,
            "penalty_level": 3,
            "penalty_label": PENALTY_LEVELS[3]["label"],
            "ban_duration_text": "Permanent",
            "notification_type": "PERMANENT_BAN",
            "notification_message": "This SIM is already permanently deactivated.",
            "risk_score": risk_score,
            "offense_count": int(current_record.get("offense_count", 3)),
            "is_permanent": True,
            "was_already_banned": True,
        }

    severity = probability_to_severity(probability)
    updated_record = record_offense(sim_id, case_id, severity=severity)
    new_offense_count = int(updated_record.get("offense_count", 1))
    penalty_level = 3 if new_offense_count >= 3 else 2 if new_offense_count == 2 else 1
    penalty = PENALTY_LEVELS[penalty_level]
    set_ban(sim_id, penalty_level)
    risk_score = calculate_risk_score(input_data, probability, new_offense_count)
    update_risk_score(sim_id, risk_score)
    log_notification(sim_id, penalty["notification_type"], penalty["notification_message"], penalty_level, penalty["ban_duration_text"])

    return {
        "sim_id": sim_id,
        "penalty_level": penalty_level,
        "penalty_label": penalty["label"],
        "ban_duration_text": penalty["ban_duration_text"],
        "notification_type": penalty["notification_type"],
        "notification_message": penalty["notification_message"],
        "risk_score": risk_score,
        "offense_count": new_offense_count,
        "is_permanent": penalty_level == 3,
        "was_already_banned": was_already_banned,
    }


def get_penalty_info(level):
    return PENALTY_LEVELS.get(level, PENALTY_LEVELS[1])
