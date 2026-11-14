# Security policy

This tool handles a wallet seed phrase, so please treat security reports seriously.

## Reporting a vulnerability

Do **not** open a public issue for security problems. Use GitHub's
"Report a vulnerability" (Security tab → Advisories) or contact the maintainer privately.

## What this tool will never do

- Send your seed phrase anywhere. The only network calls are to `https://api.hyperliquid.xyz` (`/info` and `/exchange`).
- Write your seed phrase to disk or logs.

## Warning to users

- Only ever run this code from the **official repository** and read it first (it is one short file).
- **Nobody legitimate will ask you to send them your seed phrase** or to run this tool "for you".
- Beware of forks, copies on Telegram/Discord, and look-alike repositories: a modified copy can steal your funds.
