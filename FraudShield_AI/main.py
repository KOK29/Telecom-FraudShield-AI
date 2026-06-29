import streamlit as st
import pandas as pd

from predictor import predict_fraud, explain_fraud
from protection_engine import protection_action, get_component_status, ALL_COMPONENTS, reset_all_components, unban_sim
import protection_engine as pe_module
from case_manager import create_fraud_case, resolve_case, get_all_cases, get_cases_by_sim, appeal_case
from alert_system import generate_alert
from defense_engine import enforce_defense, lift_defense, lift_all_defenses, get_defense_log
from sim_registry import register_sim, get_sim_record, get_all_sims, get_notifications, get_pending_appeals, resolve_appeal, check_ban_expired, file_appeal
from escalation_engine import calculate_risk_score
from sim_customer_registry import get_registered_sim_customer, get_all_sim_customers
from auth_manager import authenticate_user, request_password_reset, get_all_users, logout_user

st.set_page_config(page_title="Telecom FraudShield AI 2.0", page_icon="🛡️", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None


def show_auth_page():
    st.title("🛡️ Telecom FraudShield AI 2.0")
    st.subheader("Admin Access Portal")
    st.caption("Internal administrator login only.")

    login_tab, forgot_tab = st.tabs(["Login", "Forgot Password"])

    with login_tab:
        st.write("### Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):
            ok, user, message = authenticate_user(email, password)

            if ok:
                st.session_state.authenticated = True
                st.session_state.auth_user = user
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with forgot_tab:
        st.write("### Forgot Password")
        reset_email = st.text_input("Email", key="reset_email")

        if st.button("Send Password Reset Email", use_container_width=True):
            ok, message = request_password_reset(reset_email)

            if ok:
                st.info(message)
            else:
                st.error(message)



if not st.session_state.authenticated:
    show_auth_page()
    st.stop()

user = st.session_state.auth_user or {}

st.sidebar.success(f"Logged in as {user.get('email', 'admin')}")
st.sidebar.caption(f"Role: {user.get('role', 'Administrator')}")

if st.sidebar.button("Logout", use_container_width=True):
    logout_user()
    st.session_state.authenticated = False
    st.session_state.auth_user = None
    st.rerun()

st.title("🛡️ Telecom FraudShield AI 2.0")
st.subheader("AI-Powered Telecom Fraud Detection & Auto Protection System")

st.sidebar.header("SIM Card Identity")
sim_id = st.sidebar.text_input("SIM ID", value="SIM-100001", help="Enter SIM card identifier")

sim_customer = get_registered_sim_customer(sim_id) if sim_id else None
sim_is_registered = bool(sim_customer)

if sim_id:
    if sim_customer:
        st.sidebar.success("Registered SIM found")
        st.sidebar.caption(f"Customer: {sim_customer.get('full_name', 'N/A')}")
        st.sidebar.caption(f"Phone: {sim_customer.get('phone_number', 'N/A')}")
        st.sidebar.caption(f"Location: {sim_customer.get('location', 'N/A')}")
    else:
        st.sidebar.error("SIM not found in registration database")

if sim_id:
    rec = get_sim_record(sim_id)
    if rec:
        ban_level = int(rec.get("ban_level", 0))
        risk = int(rec.get("risk_score", 0))
        offenses = int(rec.get("offense_count", 0))
        if rec.get("is_permanently_blocked") in (True, "True", "true", 1, "1"):
            st.sidebar.error("🔴 PERMANENTLY DEACTIVATED")
        elif ban_level > 0:
            check_ban_expired(sim_id)
            rec = get_sim_record(sim_id)
            ban_level = int(rec.get("ban_level", 0))
            if ban_level > 0:
                st.sidebar.warning(f"⛔ BANNED — Level {ban_level}")
                st.sidebar.caption(f"Expires: {rec.get('ban_expires', 'N/A')}")
            else:
                st.sidebar.success("✅ ACTIVE")
        else:
            st.sidebar.success("✅ ACTIVE")
        st.sidebar.metric("Risk Score", f"{risk}/100")
        st.sidebar.metric("Offense Count", offenses)
    else:
        st.sidebar.info("New SIM — will register after analysis")

st.sidebar.divider()
st.sidebar.header("Live Customer Activity")
input_data = {
    "age": st.sidebar.slider("Age", 18, 75, 30),
    "account_age_days": st.sidebar.slider("Account Age Days", 1, 1500, 200),
    "calls_per_day": st.sidebar.slider("Calls Per Day", 0, 1000, 20),
    "avg_call_duration": st.sidebar.slider("Average Call Duration", 0.1, 12.0, 3.0),
    "unique_numbers_called": st.sidebar.slider("Unique Numbers Called", 1, 700, 10),
    "international_calls": st.sidebar.slider("International Calls", 0, 550, 0),
    "sms_per_day": st.sidebar.slider("SMS Per Day", 0, 1700, 20),
    "data_usage_gb": st.sidebar.slider("Data Usage GB", 0.1, 30.0, 5.0),
    "recharge_amount": st.sidebar.slider("Recharge Amount", 1, 150, 20),
    "sim_changes": st.sidebar.slider("SIM Changes", 0, 12, 0),
    "device_changes": st.sidebar.slider("Device Changes", 0, 12, 0),
    "complaints_count": st.sidebar.slider("Complaints Count", 0, 12, 0),
    "roaming_usage": st.sidebar.selectbox("Roaming Usage", [0, 1]),
    "late_payments": st.sidebar.selectbox("Late Payments", [0, 1]),
}

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Live Detection", "🛡️ Protection Center", "📁 Fraud Cases",
    "🚨 Defense Control Center", "📊 Risk & SIM Monitor", "🧑‍💼 Admin Dashboard"
])

with tab1:
    st.subheader("Registered SIM Verification")
    if sim_customer:
        st.success("SIM is registered and eligible for fraud screening.")
        st.dataframe(pd.DataFrame([sim_customer]), use_container_width=True, hide_index=True)
    else:
        st.error("This SIM is not registered. Register it in the SIM Card Registration System before running fraud analysis.")

    st.subheader("Customer Activity Input")
    st.dataframe(pd.DataFrame([input_data]), use_container_width=True, hide_index=True)
    if st.button("Analyze & Protect", use_container_width=True, disabled=not sim_is_registered):
        register_sim(sim_id)
        result = predict_fraud(input_data)
        probability = result["fraud_probability"]
        reasons = explain_fraud(input_data)
        actions = protection_action(probability, input_data)
        rec = get_sim_record(sim_id)
        offense_count = int(rec.get("offense_count", 0)) if rec else 0
        preview_risk = calculate_risk_score(input_data, probability, offense_count)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Fraud Probability", f"{probability * 100:.2f}%")
        col2.metric("ML Probability", f"{result['ml_probability'] * 100:.2f}%")
        col3.metric("Rule Score", f"{result['rule_score'] * 100:.2f}%")
        col4.metric("Risk Level", result["risk_level"])
        col5.metric("Risk Score", f"{preview_risk}/100")
        if probability >= 0.80:
            st.error("🚨 CRITICAL FRAUD THREAT DETECTED")
        elif probability >= 0.60:
            st.warning("⚠️ HIGH RISK FRAUD DETECTED")
        elif probability >= 0.35:
            st.info("🟡 SUSPICIOUS ACTIVITY DETECTED")
        else:
            st.success("✅ LOW RISK")
        st.subheader("AI Explanation")
        for reason in reasons:
            st.write("•", reason)
        st.subheader("Recommended Protective Actions")
        for action in actions:
            st.write("🛡️", action)
        defense_report = None
        case_id = pd.Timestamp.now().strftime("CASE%Y%m%d%H%M%S%f")
        if probability >= 0.35:
            st.divider()
            st.subheader("⚡ Automatic Defense Enforcement")
            defense_report = enforce_defense(case_id, probability, input_data, pe_module, sim_id=sim_id)
            tier = defense_report["threat_tier"]
            label = defense_report["threat_label"]
            status = defense_report["defense_status"]
            if tier == "CRITICAL":
                st.error(f"{label} — Defense Status: **{status}**")
            elif tier == "HIGH":
                st.warning(f"{label} — Defense Status: **{status}**")
            else:
                st.info(f"{label} — Defense Status: **{status}**")
            escalation = defense_report.get("escalation_report")
            if escalation:
                st.divider()
                st.subheader("⚡ Escalation & Penalty")
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("Penalty Level", escalation["penalty_label"])
                p2.metric("Ban Duration", escalation["ban_duration_text"])
                p3.metric("Offense Count", escalation["offense_count"])
                p4.metric("Risk Score", f"{escalation['risk_score']}/100")
                st.warning(f"📨 Notification Sent: {escalation['notification_message']}")
            blocked = defense_report.get("blocked_components", [])
            shutdown = defense_report.get("shutdown_components", [])
            if blocked:
                st.write("**Blocked / Shutdown Components**")
                badge_cols = st.columns(len(blocked))
                for i, comp in enumerate(blocked):
                    is_shutdown = comp in shutdown
                    badge_cols[i].error(f"{'🔻' if is_shutdown else '⛔'} {comp}\n\n{'SHUTDOWN' if is_shutdown else 'BLOCKED'}")
            patterns = defense_report.get("pattern_reasons", [])
            if patterns:
                st.write("**Pattern-Based Detections**")
                for p in patterns:
                    st.warning(f"⚠ {p}")
            st.write("**Live Component Status After Enforcement**")
            comp_status = get_component_status()
            status_cols = st.columns(len(ALL_COMPONENTS))
            for i, comp in enumerate(ALL_COMPONENTS):
                state = comp_status[comp]
                if state == "SHUTDOWN":
                    status_cols[i].error(f"🔻 {comp}\n\nSHUTDOWN")
                elif state == "BLOCKED":
                    status_cols[i].warning(f"⛔ {comp}\n\nBLOCKED")
                else:
                    status_cols[i].success(f"✅ {comp}\n\nACTIVE")
        if probability >= 0.35:
            case = create_fraud_case(input_data, result, actions, defense_report, sim_id=sim_id, case_id=case_id)
            alert = generate_alert(case, defense_report)
            st.divider()
            st.subheader("Fraud Case Created")
            st.success(f"Case created: **{case['case_id']}** — SIM: **{sim_id}** — Status: **{case['status']}**")
            st.subheader("Security Alert")
            st.code(alert)
        else:
            st.info("No fraud case created because risk is below Medium level.")

with tab2:
    st.subheader("Live Protection Status")
    comp_status = get_component_status()
    cols = st.columns(len(ALL_COMPONENTS))
    for i, comp in enumerate(ALL_COMPONENTS):
        state = comp_status[comp]
        if state == "SHUTDOWN":
            cols[i].error(f"🔻 {comp}\n\nSHUTDOWN")
        elif state == "BLOCKED":
            cols[i].warning(f"⛔ {comp}\n\nBLOCKED")
        else:
            cols[i].success(f"✅ {comp}\n\nACTIVE")
    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("Reset All Components", use_container_width=True):
        reset_all_components()
        st.success("All components reset to ACTIVE.")
    if col2.button("Unban Current SIM", use_container_width=True):
        unban_sim(sim_id)
        st.success(f"{sim_id} unbanned.")

with tab3:
    st.subheader("Fraud Case Database")
    filter_sim = st.text_input("Filter by SIM ID", value="", key="case_filter_sim")
    case_df = get_cases_by_sim(filter_sim) if filter_sim else get_all_cases()
    if not case_df.empty:
        st.dataframe(case_df, use_container_width=True, hide_index=True)
        selected_case = st.text_input("Enter Case ID to Resolve")
        if st.button("Resolve Case") and selected_case:
            success = resolve_case(selected_case)
            if success:
                st.success(f"Case {selected_case} resolved.")
            else:
                st.error("Case not found.")
        st.download_button("Download Fraud Cases CSV", data=case_df.to_csv(index=False), file_name="fraud_cases.csv", mime="text/csv", use_container_width=True)
    else:
        st.info("No fraud cases yet.")

with tab4:
    st.subheader("Defense Control Center")
    defense_df = get_defense_log()
    if not defense_df.empty:
        st.dataframe(defense_df, use_container_width=True, hide_index=True)
        case_id_lift = st.text_input("Case ID to Lift Defense")
        if st.button("Lift Defense"):
            lifted = lift_defense(case_id_lift, pe_module, sim_id)
            if lifted:
                st.success(f"Lifted defenses: {', '.join(lifted)}")
            else:
                st.warning("No defenses found.")
    else:
        st.info("No defense logs yet.")
    if st.button("Lift ALL Defenses", use_container_width=True):
        lifted = lift_all_defenses(pe_module)
        st.success(f"All defenses lifted: {', '.join(lifted)}")

with tab5:
    st.subheader("SIM Registry")
    sims_df = get_all_sims()
    if not sims_df.empty:
        st.dataframe(sims_df, use_container_width=True, hide_index=True)
    else:
        st.info("No SIMs registered yet.")
    st.divider()
    st.subheader("Current SIM Detail")
    current = get_sim_record(sim_id)
    if current:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("SIM ID", sim_id)
        c2.metric("Risk Score", f"{current.get('risk_score', 0)}/100")
        c3.metric("Offense Count", current.get("offense_count", 0))
        c4.metric("Ban Level", current.get("ban_level", 0))
        st.write("Appeal Status:", current.get("appeal_status", "NONE"))
        st.write("Appeal Reason:", current.get("appeal_reason", ""))
    else:
        st.info("Current SIM is not registered yet.")
    st.divider()
    st.subheader("Submit Appeal")
    appeal_text = st.text_area("Appeal Reason")
    if st.button("Submit Appeal"):
        if appeal_text.strip():
            success = file_appeal(sim_id, appeal_text)
            st.success("Appeal submitted.") if success else st.error("SIM not found.")
        else:
            st.warning("Please enter appeal reason.")
    st.divider()
    st.subheader("Notification Log")
    notif_df = get_notifications()
    if not notif_df.empty:
        st.dataframe(notif_df, use_container_width=True, hide_index=True)
    else:
        st.info("No notifications yet.")

with tab6:
    st.subheader("🧑‍💼 Professional Admin Dashboard")
    st.caption("Central control panel for fraud operations, SIM risk, appeals, and enforcement activity.")
    with st.expander("Admin Users", expanded=False):
        users_df = get_all_users()
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True, hide_index=True)
        else:
            st.info("No admin users found.")
    cases_df = get_all_cases()
    sims_df = get_all_sims()
    defense_df = get_defense_log()
    notif_df = get_notifications()
    appeals_df = get_pending_appeals()

    total_cases = len(cases_df) if not cases_df.empty else 0
    total_sims = len(sims_df) if not sims_df.empty else 0
    pending_appeals = len(appeals_df) if not appeals_df.empty else 0
    high_cases = len(cases_df[cases_df["risk_level"].isin(["High", "Critical"])]) if not cases_df.empty else 0
    critical_cases = len(cases_df[cases_df["risk_level"] == "Critical"]) if not cases_df.empty else 0
    banned_sims = len(sims_df[sims_df["ban_level"].astype(int) > 0]) if not sims_df.empty else 0
    permanent_sims = len(sims_df[sims_df["is_permanently_blocked"].isin([True, "True", "true", 1, "1"])]) if not sims_df.empty else 0

    st.write("### Executive Summary")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Cases", total_cases)
    m2.metric("Total SIMs", total_sims)
    m3.metric("High/Critical", high_cases)
    m4.metric("Critical", critical_cases)
    m5.metric("Banned SIMs", banned_sims)
    m6.metric("Pending Appeals", pending_appeals)

    st.divider()
    st.write("### Registered SIM Customers")
    customer_df = get_all_sim_customers()
    if not customer_df.empty:
        st.dataframe(customer_df, use_container_width=True, hide_index=True)
    else:
        st.info("No registered SIM customers found.")

    st.divider()
    st.write("### Fraud Operations Overview")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("#### Risk Level Distribution")
        if not cases_df.empty and "risk_level" in cases_df.columns:
            risk_counts = cases_df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            st.bar_chart(risk_counts.set_index("Risk Level"))
        else:
            st.info("No fraud case data available.")
    with col_b:
        st.write("#### Case Status Distribution")
        if not cases_df.empty and "status" in cases_df.columns:
            status_counts = cases_df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"))
        else:
            st.info("No case status data available.")

    st.divider()
    st.write("### SIM Risk Intelligence")
    if not sims_df.empty:
        risky_sims = sims_df.copy()
        risky_sims["risk_score"] = risky_sims["risk_score"].astype(int)
        risky_sims = risky_sims.sort_values("risk_score", ascending=False)
        available_cols = [c for c in ["sim_id", "risk_score", "offense_count", "ban_level", "is_permanently_blocked", "appeal_status", "last_offense_at"] if c in risky_sims.columns]
        st.dataframe(risky_sims[available_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No SIM records available.")

    st.divider()
    st.write("### Recent Fraud Cases")
    if not cases_df.empty:
        recent_cols = ["case_id", "sim_id", "created_at", "fraud_probability", "risk_level", "fraud_status", "status", "penalty_level", "risk_score"]
        available_recent_cols = [c for c in recent_cols if c in cases_df.columns]
        st.dataframe(cases_df[available_recent_cols].head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No fraud cases yet.")

    st.divider()
    st.write("### Appeal Review Center")
    if not appeals_df.empty:
        st.dataframe(appeals_df, use_container_width=True, hide_index=True)
        review_sim = st.selectbox("Select SIM to review", appeals_df["sim_id"].tolist(), key="admin_dashboard_review_sim")
        selected_appeal = appeals_df[appeals_df["sim_id"] == review_sim].iloc[0]
        st.info(f"Appeal Reason: {selected_appeal.get('appeal_reason', 'N/A')}")
        approve_col, deny_col = st.columns(2)
        with approve_col:
            if st.button("✅ Approve Appeal", use_container_width=True, key="admin_dash_approve"):
                resolve_appeal(review_sim, approved=True)
                unban_sim(review_sim)
                st.success(f"Appeal approved for {review_sim}.")
                st.rerun()
        with deny_col:
            if st.button("❌ Deny Appeal", use_container_width=True, key="admin_dash_deny"):
                resolve_appeal(review_sim, approved=False)
                st.error(f"Appeal denied for {review_sim}.")
                st.rerun()
    else:
        st.success("No pending appeals.")

    st.divider()
    st.write("### Enforcement Activity")
    if not defense_df.empty:
        st.dataframe(defense_df.head(20), use_container_width=True, hide_index=True)
    else:
        st.info("No defense activity recorded yet.")

    st.divider()
    st.write("### Admin Report Downloads")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        if not cases_df.empty:
            st.download_button("Download Cases CSV", cases_df.to_csv(index=False), "fraud_cases_report.csv", "text/csv", use_container_width=True)
    with d2:
        if not sims_df.empty:
            st.download_button("Download SIM Registry CSV", sims_df.to_csv(index=False), "sim_registry_report.csv", "text/csv", use_container_width=True)
    with d3:
        if not defense_df.empty:
            st.download_button("Download Defense Logs CSV", defense_df.to_csv(index=False), "defense_logs_report.csv", "text/csv", use_container_width=True)
    with d4:
        if not notif_df.empty:
            st.download_button("Download Notifications CSV", notif_df.to_csv(index=False), "notifications_report.csv", "text/csv", use_container_width=True)
