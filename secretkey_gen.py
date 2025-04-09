import secrets

# Generate a secure random 256-bit (32-byte) secret key
secret_key = secrets.token_urlsafe(32)  # Generates a URL-safe base64 string
print("Generated new URL-Safe secret Key: ", secret_key)
