import dataiku


def get_my_secret_key(secret_key_name: str)->str:
    """Retrieves the secret key of a user, based on it's name.
    Secret keys are defined in 'Profile and settings'/'My Account'/'Other credentials'

    :returns: secret_key_name: str: The requested secret key. 
    """
    client = dataiku.api_client()
    secret_key = None
    for secret in client.get_auth_info(with_secrets=True)["secrets"]:
        if secret["key"] == secret_key_name:
            secret_key = secret["value"]
    if secret_key is None:
        raise Exception("Secret key not found!")
    return secret_key