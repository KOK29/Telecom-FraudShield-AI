import streamlit as st

from sim_registry import (
    register_sim_customer,
    get_all_sim_customers,
    search_sim_customer,
    delete_sim_customer,
)

st.set_page_config(
    page_title="SIM Card Registration System",
    page_icon="📝",
    layout="wide",
)

st.title("📝 SIM Card Registration System")
st.caption("Register customer SIM information before FraudShield AI can run fraud checks on that SIM.")

tab1, tab2, tab3 = st.tabs([
    "📝 Register SIM",
    "📋 Registered Customers",
    "🔎 Search / Manage",
])


with tab1:
    st.subheader("Register New SIM Customer")

    with st.form("sim_register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            sim_id = st.text_input("SIM ID *", placeholder="Example: SIM-100001")
            full_name = st.text_input("Customer Full Name *", placeholder="Example: Zwe Mun Wint Thu")
            nrc = st.text_input("NRC / National ID *", placeholder="Example: 12/ABC(N)123456")

        with col2:
            location = st.text_input("Location *", placeholder="Example: Yangon")
            phone_number = st.text_input("Phone Number", placeholder="Example: 09xxxxxxxxx")
            email = st.text_input("Email", placeholder="Example: customer@email.com")
            status = st.selectbox("SIM Status", ["ACTIVE", "SUSPENDED", "CANCELLED"])

        submitted = st.form_submit_button("Register SIM", use_container_width=True)

        if submitted:
            if not sim_id.strip() or not full_name.strip() or not nrc.strip() or not location.strip():
                st.error("Please fill all required fields: SIM ID, Name, NRC, and Location.")
            else:
                register_sim_customer(
                    sim_id=sim_id.strip(),
                    full_name=full_name.strip(),
                    nrc=nrc.strip(),
                    location=location.strip(),
                    phone_number=phone_number.strip(),
                    email=email.strip(),
                    status=status,
                )
                st.success(f"SIM {sim_id.strip()} registered successfully for {full_name.strip()}.")


with tab2:
    st.subheader("Registered SIM Customers")

    df = get_all_sim_customers()

    if not df.empty:
        st.metric("Total Registered SIMs", len(df))

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False),
            file_name="registered_sim_customers.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("No SIM customers registered yet.")


with tab3:
    st.subheader("Search and Manage SIM Customers")

    keyword = st.text_input("Search by SIM ID, Name, NRC, Location, or Phone Number")

    result_df = search_sim_customer(keyword)

    if not result_df.empty:
        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.write("### Delete SIM Record")

        selected_sim = st.selectbox(
            "Select SIM ID to delete",
            result_df["sim_id"].tolist(),
        )

        confirm = st.checkbox("I confirm I want to delete this SIM record")

        if st.button("Delete Selected SIM", type="primary", use_container_width=True):
            if confirm:
                deleted = delete_sim_customer(selected_sim)
                if deleted:
                    st.success(f"SIM {selected_sim} deleted successfully.")
                    st.rerun()
                else:
                    st.error("Delete failed or SIM not found.")
            else:
                st.warning("Please confirm before deleting.")
    else:
        st.info("No matching SIM records found.")
