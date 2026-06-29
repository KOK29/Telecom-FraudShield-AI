import re
import pandas as pd
from supabase_client import get_supabase


def validate_password(password):
    if re.fullmatch(r"(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,}", password or ""):
        return True, "Password is valid."
    return False, "Password must contain at least 8 characters, 1 uppercase letter, 1 number, and 1 special character."


def validate_email(email):
    email = (email or "").strip().lower()
    if re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
        return True, "Email is valid."
    return False, "Please enter a valid email address."


def create_user(email, password, full_name="", role="Administrator"):
    email = email.strip().lower()

    email_ok, email_msg = validate_email(email)
    if not email_ok:
        return False, email_msg

    password_ok, password_msg = validate_password(password)
    if not password_ok:
        return False, password_msg

    try:
        get_supabase().auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": role
                }
            }
        })

        return True, "Admin account created. Check email to confirm account."

    except Exception as e:
        return False, f"Create account failed: {e}"


def authenticate_user(email, password):
    email = email.strip().lower()

    try:
        response = get_supabase().auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = response.user

        safe_user = {
            "id": user.id,
            "username": user.email,
            "email": user.email,
            "full_name": user.user_metadata.get("full_name", ""),
            "role": user.user_metadata.get("role", "Administrator"),
        }

        return True, safe_user, "Login successful."

    except Exception:
        return False, None, "Wrong email/password or email not confirmed yet."


def request_password_reset(email):
    email = email.strip().lower()

    try:
        get_supabase().auth.reset_password_for_email(email)
        return True, "Password reset email sent."
    except Exception as e:
        return False, str(e)


def logout_user():
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass


def get_all_users():
    return pd.DataFrame()