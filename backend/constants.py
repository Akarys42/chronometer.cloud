import datetime
import os


def get_required_env_var(var_name: str) -> str:
    """Retrieve a required environment variable or raise an error if not set."""
    value = os.environ.get(var_name)

    if value is None:
        raise EnvironmentError(f"Required environment variable '{var_name}' is not set.")

    return value


MONGO_URI = get_required_env_var("MONGO_URI")
MONGO_DATABASE = get_required_env_var("MONGO_DATABASE")

ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")
FAILED_PASSWORD_BAN = datetime.timedelta(minutes=1)

CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

EXPIRATION = 7 * 24 * 60 * 60  # 7 days in seconds
CLOUDFLARE_GRAPHQL_ENDPOINT = "https://api.cloudflare.com/client/v4/graphql"
