"""Offline tests: no network, no real keys. Run with:  python -m pytest -q"""
import builtins
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import withdraw_from_vault as W  # noqa: E402

# Public test mnemonic (Hardhat/Anvil default). NEVER use it for real funds.
MNEMONIC = "test test test test test test test test test test test junk"
VAULT = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"


def _run(inputs, max_withdrawable="12.345678", mnemonic=MNEMONIC):
    it = iter(inputs)
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json))
        resp = mock.Mock()
        resp.raise_for_status = lambda: None
        if json.get("type") == "vaultDetails":
            resp.json = lambda: {"maxWithdrawable": max_withdrawable}
        else:
            resp.json = lambda: {"status": "ok", "response": {"type": "default"}}
        return resp

    with mock.patch.object(W, "getpass", lambda _p: mnemonic), \
         mock.patch.object(builtins, "input", lambda _p="": next(it)), \
         mock.patch.object(W.requests, "post", fake_post):
        W.main()
    return calls


def test_withdraws_max_minus_default_reserve():
    calls = _run([VAULT, "", "WITHDRAW"])
    exchange = calls[1][1]
    assert exchange["action"] == {
        "type": "vaultTransfer",
        "vaultAddress": VAULT,
        "isDeposit": False,
        "usd": 11_845_678,
    }
    assert set(exchange["signature"]) == {"r", "s", "v"}


def test_custom_reserve_zero_withdraws_everything():
    calls = _run([VAULT, "0", "WITHDRAW"])
    assert calls[1][1]["action"]["usd"] == 12_345_678


def test_cancel_sends_nothing():
    calls = _run([VAULT, "", "no"])
    assert len(calls) == 1  # only the /info call


def test_nothing_to_withdraw():
    calls = _run([VAULT, "", ], max_withdrawable="0.3")
    assert len(calls) == 1


def test_invalid_vault_address():
    with mock.patch.object(builtins, "input", lambda _p="": "0x123"):
        try:
            W.prompt_vault_address()
        except ValueError:
            return
    raise AssertionError("expected ValueError")
