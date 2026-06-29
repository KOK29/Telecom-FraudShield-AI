def _severity_header(defense_report):
    if defense_report and defense_report.get("threat_label"):
        return defense_report["threat_label"]
    return "🟢 LOW"


def _format_blocked_list(components):
    if not components:
        return "  None"
    return "\n".join(f"  ⛔ {comp}" for comp in components)


def _format_shutdown_list(components):
    if not components:
        return "  None"
    return "\n".join(f"  🔻 {comp}" for comp in components)


def generate_alert(case, defense_report=None):
    severity = _severity_header(defense_report)
    alert = f"""
{'═' * 52}
  🚨 FRAUD ALERT — {severity}
{'═' * 52}

Case ID:           {case.get('case_id', 'N/A')}
SIM ID:            {case.get('sim_id', 'N/A')}
Created At:        {case.get('created_at', 'N/A')}

Risk Level:        {case.get('risk_level', 'N/A')}
Fraud Status:      {case.get('fraud_status', 'N/A')}
Fraud Probability: {case.get('fraud_probability', 'N/A')}%
Risk Score:        {case.get('risk_score', 'N/A')}/100

Protective Actions:
  {case.get('actions', 'No action assigned')}

Case Status:       {case.get('status', 'N/A')}
"""
    if defense_report:
        blocked_section = _format_blocked_list(defense_report.get("blocked_components", []))
        shutdown_section = _format_shutdown_list(defense_report.get("shutdown_components", []))
        pattern_reasons = defense_report.get("pattern_reasons", [])
        reasons_section = "\n".join(f"  ⚠ {r}" for r in pattern_reasons) if pattern_reasons else "  None"
        alert += f"""
{'─' * 52}
  🛡️ DEFENSE ENFORCEMENT DETAILS
{'─' * 52}

Defense Status:    {defense_report.get('defense_status', 'N/A')}
Threat Tier:       {defense_report.get('threat_tier', 'N/A')}
Enforced At:       {defense_report.get('enforcement_timestamp', 'N/A')}

Blocked Components:
{blocked_section}

Shutdown Components:
{shutdown_section}

Pattern-Based Detections:
{reasons_section}
"""
        penalty_level = defense_report.get("penalty_level")
        if penalty_level:
            alert += f"""
{'─' * 52}
  ⚡ ESCALATION & PENALTY DETAILS
{'─' * 52}

Penalty Level:     {defense_report.get('penalty_label', f'Level {penalty_level}')}
Ban Duration:      {defense_report.get('ban_duration_text', 'N/A')}
Offense Count:     {defense_report.get('offense_count', 0)}
Risk Score:        {defense_report.get('risk_score', 'N/A')}/100

📨 Notification Sent:
  {defense_report.get('notification_message', '')}

📋 Appeal Instructions:
  If this action was taken in error, submit an appeal through the FraudShield dashboard.
"""
    alert += f"\n{'═' * 52}\n"
    return alert
