import os

# DocuSign JWT settings, read from pdf_filler/.env (see .env.example)
DS_JWT = {
    "ds_client_id": os.getenv("DS_CLIENT_ID"),
    "ds_impersonated_user_id": os.getenv("DS_IMPERSONATED_USER_ID"),  # The id of the user.
    # Path to the RSA private key (relative to pdf_filler/src). The key file itself is git-ignored.
    "private_key_file": os.getenv("DS_PRIVATE_KEY_FILE", "./third_party/docu_sign/app/private.key"),
    "authorization_server": os.getenv("DS_AUTH_SERVER", "account-d.docusign.com"),
}
