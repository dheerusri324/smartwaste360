# backend/hash_password.py
import bcrypt

# The password you want to use for your test user
password_to_hash = "password123"

# Generate the hash
hashed_password = bcrypt.hashpw(
    password_to_hash.encode('utf-8'), 
    bcrypt.gensalt()
).decode('utf-8')

print("\n--- COPY YOUR HASHED PASSWORD BELOW ---\n")
print(hashed_password)
print("\n---------------------------------------\n")