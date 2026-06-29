FraudShield AI + SIM Registration Integration

What changed:
1. Added sim_customers table support.
2. FraudShield now checks whether a SIM exists in sim_customers before allowing Analyze & Protect.
3. FraudShield sidebar now shows registered customer details.
4. Admin Dashboard now shows registered SIM customers.
5. SIM Registration app now saves SIM customer data into the same Supabase project.
6. Supabase schema now includes sim_customers and admin_users.

Setup steps:
1. Open Supabase SQL Editor.
2. Run FraudShield_AI/supabase_schema.sql.
3. Choose Run without RLS if Supabase asks.
4. In FraudShield_AI, make sure .env contains SUPABASE_URL and SUPABASE_KEY.
5. In SIM_Card_Registration_Project, make sure .env contains the same SUPABASE_URL and SUPABASE_KEY.
6. Run the admin creation script once:
   python create_admin_account.py
7. Run the SIM registration system:
   python -m streamlit run main.py
   Register a SIM, for example SIM-100001.
8. Run FraudShield AI:
   python -m streamlit run main.py
   Login, enter the same SIM ID, then run Analyze & Protect.

Important:
- Use the same sim_id in both systems.
- FraudShield blocks analysis if the SIM is not registered in sim_customers.
- This creates a complete workflow: SIM Registration -> Supabase -> FraudShield AI -> Fraud Case / Defense / Appeal records.
