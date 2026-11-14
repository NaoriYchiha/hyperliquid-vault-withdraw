# hyperliquid-vault-withdraw

A tiny, single-file, open-source command-line tool to **withdraw your USDC from a Hyperliquid vault directly through the Hyperliquid API** — for when the web UI won't let you.

> ⚠️ **Unofficial tool. Not affiliated with Hyperliquid.** Use at your own risk. Read the [Security](#security-read-this-first) section before you type your seed phrase anywhere.

## What it does

1. Asks for your wallet's BIP-39 seed phrase (hidden input, kept in memory only).
2. Asks for the vault address.
3. Queries Hyperliquid for the maximum amount **you** can currently withdraw from that vault.
4. Shows you the amount and asks for explicit confirmation (`WITHDRAW`).
5. Signs a standard `vaultTransfer` (withdrawal) action locally and submits it to `https://api.hyperliquid.xyz/exchange`.

It uses the official [`hyperliquid-python-sdk`](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) for signing. Nothing is sent anywhere except Hyperliquid's API. The whole logic is ~150 lines in [`withdraw_from_vault.py`](withdraw_from_vault.py) — **please read it before running**.

## Requirements

- Python 3.10+
- The wallet (seed phrase) that **deposited** into the vault (or the vault leader's wallet)

## Installation

```bash
git clone https://github.com/NaoriYchiha/hyperliquid-vault-withdraw.git
cd hyperliquid-vault-withdraw
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Usage

```bash
python withdraw_from_vault.py
```

Example session:

```
Enter your wallet seed phrase (input is hidden):
Enter the Hyperliquid vault address: 0x...

Wallet address: 0xYourAddress
Vault address:  0x...
Maximum withdrawable: 123.456789 USDC
USDC to leave in the vault [0.5]:

Amount to withdraw: 122.956789 USDC
Remaining reserve:  0.5 USDC

Type WITHDRAW to submit the vault withdrawal:
```

**Always check that the printed `Wallet address` is the address you deposited from.**

### Reserve

By default the script leaves **0.5 USDC** in the vault. Press Enter to accept, or type another amount (`0` to try to withdraw everything).

### Funds arrive on Hyperliquid, not in your wallet

A vault withdrawal moves USDC back to your **Hyperliquid account** (perps/spot balance). It does not send funds to your wallet on Arbitrum. To move them out you still need a second step: a normal withdrawal from your Hyperliquid account.

#### Withdrawing from your Hyperliquid account with Rabby Wallet

If the Hyperliquid website is blocked or unavailable for you, you can do this second step with [Rabby Wallet](https://rabby.io), which has Hyperliquid built in:

1. Install Rabby **only from the official site or your browser's official store listing**, and import/connect the same wallet you used above (the one whose address the script printed).
2. Open the **Perps** tab in Rabby.
3. Make sure the USDC from the vault shows up as your Perps balance (it may take a moment after the vault withdrawal).
4. Choose **Withdraw** and send the USDC to your wallet on Arbitrum.

The exact buttons and wording in Rabby may change between versions. A small withdrawal fee may be charged by Hyperliquid, so very small balances may not be worth withdrawing.

> Importing your seed phrase into any wallet app carries the same risk as using this script. Download Rabby only from official sources and check the URL carefully.

## Limitations

- Only the **first account** derived from the seed phrase (`m/44'/60'/0'/0/0`) is used. This matches the first account in MetaMask and most wallets. Other account indexes and custom derivation paths are not supported.
- Hardware wallets are not supported (the tool needs the seed phrase).
- **Mainnet only.**
- Hyperliquid enforces its own rules (e.g. lock-up periods after depositing, minimum leader share). If `maxWithdrawable` is `0` or the API returns an error, the protocol is refusing the withdrawal — this tool cannot override it. Check Hyperliquid's documentation for current rules.
- If Hyperliquid changes its API, the script may stop working. Please open an issue.

## Security (read this first)

You are being asked to type a seed phrase. That is the single most dangerous thing you can do in crypto, so:

- **Read the code** (`withdraw_from_vault.py`). It's short. The only network calls go to `api.hyperliquid.xyz`.
- **Only download from the official repository.** Copies and forks can be modified to steal your seed phrase.
- **Nobody will ever need to receive your seed phrase** to help you. Anyone asking for it is a scammer.
- Run it on a **clean, trusted computer**, ideally in a fresh virtual environment, with no screen sharing or remote-access tools running.
- **Pin and verify dependencies** (`requirements.txt` is pinned). Install only from PyPI.
- After use, consider moving your remaining funds to a new wallet if you have any doubt about the security of the machine you used.
- Test first with a small vault position if possible.

The seed phrase is read with `getpass`, is never written to disk or printed, and exists only in process memory while the script runs.

## Development

```bash
pip install pytest
python -m pytest -q
```

Tests are fully offline (the API is mocked) and use the public Hardhat test mnemonic.

## Disclaimer

This software is provided "as is", without warranty of any kind. It is a convenience tool for withdrawing **your own** funds using Hyperliquid's public API. You are solely responsible for complying with applicable laws, sanctions and Hyperliquid's terms of use. The authors are not responsible for any loss of funds.

## License

[MIT](LICENSE)

