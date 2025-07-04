import json
import os

def load_config():
    """
    Load configuration from either environment variables or config.json file.
    Environment variables take precedence over config file.
    """
    # Try environment variables first (more secure)
    account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")
    secret_key = os.getenv("HYPERLIQUID_SECRET_KEY")
    is_mainnet = os.getenv("HYPERLIQUID_IS_MAINNET", "true").lower() == "true"
    
    # If environment variables are not set, try config file
    if not account_address or not secret_key:
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                account_address = account_address or config.get("account_address")
                secret_key = secret_key or config.get("secret_key")
                is_mainnet = config.get("is_mainnet", True) if is_mainnet else is_mainnet
        except FileNotFoundError:
            raise FileNotFoundError(
                "Configuration not found. Please either:\n"
                "1. Set environment variables: HYPERLIQUID_ACCOUNT_ADDRESS, HYPERLIQUID_SECRET_KEY, HYPERLIQUID_IS_MAINNET\n"
                "2. Create a config.json file with your credentials"
            )
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in config.json file")
    
    if not account_address or not secret_key:
        raise ValueError("Account address and secret key are required")
    
    return {
        "account_address": account_address,
        "secret_key": secret_key,
        "is_mainnet": is_mainnet
    }
