from predictor import predict_fraud
from escalation_engine import calculate_risk_score

fraud_data = {
    "age": 25,
    "account_age_days": 20,
    "calls_per_day": 850,
    "avg_call_duration": 0.5,
    "unique_numbers_called": 500,
    "international_calls": 350,
    "sms_per_day": 1200,
    "data_usage_gb": 5,
    "recharge_amount": 10,
    "sim_changes": 7,
    "device_changes": 6,
    "complaints_count": 8,
    "roaming_usage": 1,
    "late_payments": 1,
}

result = predict_fraud(fraud_data)
score = calculate_risk_score(fraud_data, result["fraud_probability"], 0)

print("Fraud Probability:", round(result["fraud_probability"] * 100, 2), "%")
print("ML Probability:", round(result["ml_probability"] * 100, 2), "%")
print("Rule Score:", round(result["rule_score"] * 100, 2), "%")
print("Risk Level:", result["risk_level"])
print("Fraud Status:", result["fraud_status"])
print("Risk Score:", score, "/100")

assert result["fraud_probability"] >= 0.60
assert result["risk_level"] in ["High", "Critical"]
print("Test passed.")
