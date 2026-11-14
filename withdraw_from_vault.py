"""
Withdraw USDC from a Hyperliquid vault to the vault owner's account.

The script interactively asks for:
1. The owner's BIP-39 seed phrase.
2. The vault address.

The seed phrase is entered locally and is not saved to disk.
"""

import sys
import time
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from getpass import getpass

import requests
from eth_account import Account
from eth_utils import is_address
from hyperliquid.utils import constants
from hyperliquid.utils.signing import sign_l1_action


API_URL = constants.MAINNET_API_URL
INFO_URL = f"{API_URL}/info"
EXCHANGE_URL = f"{API_URL}/exchange"
USDC_DECIMALS = 6
USDC_SCALE = 10 ** USDC_DECIMALS
DEFAULT_RESERVE = Decimal("0.5")


def prompt_wallet():
    mnemonic = getpass("Enter your wallet seed phrase (input is hidden): ").strip()

    if not mnemonic:
        raise ValueError("Seed phrase cannot be empty.")

    # Enable mnemonic-based wallet derivation in eth-account.
    Account.enable_unaudited_hdwallet_features()

    try:
        return Account.from_mnemonic(mnemonic)
    except Exception as exc:
        raise ValueError(
            "Could not derive a wallet from this seed phrase. "
            "Check the words and wallet derivation path."
        ) from exc


def prompt_vault_address():
    address = input("Enter the Hyperliquid vault address: ").strip()

    if not is_address(address):
        raise ValueError("The vault address is not a valid EVM address.")

    return address


def get_max_withdrawable(vault_address, wallet_address):
    response = requests.post(
        INFO_URL,
        json={
            "type": "vaultDetails",
            "vaultAddress": vault_address,
            "user": wallet_address,
        },
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    if "maxWithdrawable" not in data:
        raise RuntimeError(f"Unexpected API response: {data}")

    try:
        return Decimal(str(data["maxWithdrawable"]))
    except InvalidOperation as exc:
        raise RuntimeError("Invalid maxWithdrawable value returned by the API.") from exc


def main():
    wallet = prompt_wallet()
    vault_address = prompt_vault_address()

    print(f"\nWallet address: {wallet.address}")
    print(f"Vault address:  {vault_address}")

    max_withdrawable = get_max_withdrawable(vault_address, wallet.address)
    print(f"Maximum withdrawable: {max_withdrawable} USDC")

    reserve_input = input(
        f"USDC to leave in the vault [{DEFAULT_RESERVE}]: "
    ).strip()

    try:
        reserve = Decimal(reserve_input) if reserve_input else DEFAULT_RESERVE
    except InvalidOperation as exc:
        raise ValueError("Enter a valid reserve amount.") from exc

    if not reserve.is_finite() or reserve < 0:
        raise ValueError("Reserve must be zero or greater.")

    amount = (max_withdrawable - reserve).quantize(
        Decimal("0.000001"), rounding=ROUND_DOWN
    )

    if amount <= 0:
        print("Nothing to withdraw after applying the reserve.")
        return

    print(f"\nAmount to withdraw: {amount} USDC")
    print(f"Remaining reserve:  {reserve} USDC")

    confirmation = input(
        "\nType WITHDRAW to submit the vault withdrawal: "
    ).strip()

    if confirmation != "WITHDRAW":
        print("Cancelled. No transaction was submitted.")
        return

    # Hyperliquid vaultTransfer uses integer micro-USDC units.
    action = {
        "type": "vaultTransfer",
        "vaultAddress": vault_address.lower(),
        "isDeposit": False,
        "usd": int(amount * USDC_SCALE),
    }

    nonce = int(time.time() * 1000)
    signature = sign_l1_action(wallet, action, None, nonce, None, True)

    response = requests.post(
        EXCHANGE_URL,
        json={
            "action": action,
            "nonce": nonce,
            "signature": signature,
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()

    print("\nHyperliquid response:")
    print(result)

    if result.get("status") == "err":
        raise RuntimeError(f"Vault withdrawal failed: {result}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, requests.RequestException) as error:
        print(f"\nError: {error}", file=sys.stderr)
        sys.exit(1)
