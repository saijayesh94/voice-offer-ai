from os import path
import sys
import subprocess

from docusign_esign import ApiClient
from docusign_esign.client.api_exception import ApiException
from third_party.docu_sign.app.jwt_helpers import get_jwt_token, get_private_key
from third_party.docu_sign.app.eSignature.examples.eg002_signing_via_email import Eg002SigningViaEmailController
from third_party.docu_sign.app.jwt_config import DS_JWT

# pip install DocuSign SDK
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'docusign_esign'])

SCOPES = [
    "signature", "impersonation"
]


def get_consent_url():
    url_scopes = "+".join(SCOPES)

    # Construct consent URL
    redirect_uri = "https://developers.docusign.com/platform/auth/consent"
    consent_url = f"https://{DS_JWT['authorization_server']}/oauth/auth?response_type=code&" \
                  f"scope={url_scopes}&client_id={DS_JWT['ds_client_id']}&redirect_uri={redirect_uri}"

    return consent_url


def get_token(private_key, api_client):
    # Call request_jwt_user_token method
    token_response = get_jwt_token(private_key, SCOPES, DS_JWT["authorization_server"], DS_JWT["ds_client_id"],
                                   DS_JWT["ds_impersonated_user_id"])
    access_token = token_response.access_token

    # Save API account ID
    user_info = api_client.get_user_info(access_token)
    accounts = user_info.get_accounts()
    api_account_id = accounts[0].account_id
    base_path = accounts[0].base_uri + "/restapi"

    return {"access_token": access_token, "api_account_id": api_account_id, "base_path": base_path}


def get_args(api_account_id, access_token, base_path, envelope_args):

    envelope_args = {
        "signer_email": envelope_args["signer_email"],
        "signer_name": envelope_args["signer_name"],
        "cc_email": envelope_args["cc_email"],
        "cc_name": envelope_args["cc_name"],
        "status": "sent",
    }
    args = {
        "account_id": api_account_id,
        "base_path": base_path,
        "access_token": access_token,
        "envelope_args": envelope_args
    }

    return args


def run_example(private_key, api_client, envelope_args, config_dict):
    jwt_values = get_token(private_key, api_client)
    args = get_args(jwt_values["api_account_id"], jwt_values["access_token"], jwt_values["base_path"], envelope_args)
    for index in range(len(config_dict["files"])):
        print("Length:", len(config_dict["files"]))
        file_info = config_dict["files"][index]
        envelope_id = Eg002SigningViaEmailController.worker(args, config_dict, file_info)
        print("Your envelope has been sent.")
        print(envelope_id)


def docu_sign(envelope_args, config_dict):
    api_client = ApiClient()
    api_client.set_base_path(DS_JWT["authorization_server"])
    api_client.set_oauth_host_name(DS_JWT["authorization_server"])

    private_key = get_private_key(DS_JWT["private_key_file"]).encode("ascii").decode("utf-8")

    try:
        run_example(private_key, api_client, envelope_args, config_dict)
    except ApiException as err:
        body = err.body.decode('utf8')

        if "consent_required" in body:
            consent_url = get_consent_url()
            print("Open the following URL in your browser to grant consent to the application:")
            print(consent_url)
            consent_granted = input("Consent granted? Select one of the following: \n 1)Yes \n 2)No \n")
            if consent_granted == "1":
                run_example(private_key, api_client, envelope_args, config_dict)
            else:
                sys.exit("Please grant consent")


# envelope_args = {
#     "signer_email": "chirag@deepnetlabs.com",
#     "signer_name": "chirag",
#     "cc_email": "kalyan@deepnetlabs.com",
#     "cc_name": "kalyan"
# }

# main(envelope_args)
