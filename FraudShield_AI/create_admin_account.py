from auth_manager import create_user

user = "Zwe Mun"
email = "zwemunwintthu29@gmail.com"
password = "Zwemun29#"
full_name = "System Administrator"
role = "Administrator"

ok, message = create_user(email, password, full_name, role)

print(message)

if ok:
    print("Email:", email)
    print("Password:", password)