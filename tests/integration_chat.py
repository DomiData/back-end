#!/usr/bin/env python3
"""
Integration test for chat TTLCache session management.

Starts a minimal uvicorn server (just the chat router, no DB/Firebase lifespan)
and makes real HTTP POST requests to verify cache behaviour.

Usage:
    python3 tests/integration_chat.py              # basic tests
    python3 tests/integration_chat.py --ttl        # also run the TTL expiry test (~7s extra)

Endpoints used:
    POST   /chat/test-session?uid=<uid>    (no auth required, uses _chat_histories cache)
    GET    /debug/history/<uid>            (inspect cache state — test server only)
    DELETE /debug/history/<uid>            (evict a UID from the cache — test server only)
    GET    /debug/cache-info               (TTLCache metadata)

Requirements:
    - OPENAI_API_KEY set in .env or environment
    - pip install cachetools requests uvicorn
"""

import os
import subprocess
import sys
import time

import requests

HOST = "http://127.0.0.1:8787"
REQUEST_TIMEOUT = 60  # seconds — OpenAI can be slow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def post(message: str, uid: str) -> dict:
    resp = requests.post(
        f"{HOST}/chat/test-session",
        params={"uid": uid},
        json={"message": message},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def get_history(uid: str) -> dict:
    resp = requests.get(f"{HOST}/debug/history/{uid}", timeout=5)
    resp.raise_for_status()
    return resp.json()


def clear_history(uid: str) -> None:
    requests.delete(f"{HOST}/debug/history/{uid}", timeout=5)


def cache_info() -> dict:
    resp = requests.get(f"{HOST}/debug/cache-info", timeout=5)
    resp.raise_for_status()
    return resp.json()


def wait_for_server(timeout: int = 20) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(f"{HOST}/docs", timeout=1)
            return True
        except Exception:
            time.sleep(0.4)
    return False


def _ok(label: str) -> None:
    print(f"  [PASS] {label}")


def _fail(label: str, detail: str = "") -> None:
    print(f"  [FAIL] {label}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_cache_type() -> bool:
    """_chat_histories is a TTLCache with the expected parameters."""
    try:
        info = cache_info()
        assert info["type"] == "TTLCache", f"expected TTLCache, got {info['type']}"
        assert info["maxsize"] == 500, f"expected maxsize=500, got {info['maxsize']}"
        assert info["ttl"] == 1200, f"expected ttl=1200, got {info['ttl']}"
        _ok(f"cache type — TTLCache(maxsize={info['maxsize']}, ttl={info['ttl']})")
        return True
    except Exception as e:
        _fail("cache type", str(e))
        return False


def test_connectivity() -> bool:
    """Server is reachable and returns a valid response."""
    uid = "conn-test"
    clear_history(uid)
    try:
        r = post("Olá!", uid=uid)
        assert "answer" in r and "disclaimer" in r
        _ok(f"connectivity — answer: {r['answer'][:80]}...")
        return True
    except Exception as e:
        _fail("connectivity", str(e))
        return False


def test_history_accumulation() -> bool:
    """Cache entries grow with each request for the same UID."""
    uid = "history-test"
    clear_history(uid)
    try:
        # Before any request — cache should be empty
        before = get_history(uid)
        assert before["count"] == 0, f"expected empty cache, got {before}"

        post("Primeira mensagem.", uid=uid)

        # After request 1 — 2 entries (human + ai)
        after_1 = get_history(uid)
        assert after_1["count"] == 2, (
            f"expected 2 entries after msg 1, got {after_1['count']}"
        )
        assert after_1["history"][0] == ["human", "Primeira mensagem."]

        post("Segunda mensagem.", uid=uid)

        # After request 2 — 4 entries
        after_2 = get_history(uid)
        assert after_2["count"] == 4, (
            f"expected 4 entries after msg 2, got {after_2['count']}"
        )

        _ok("history accumulation — cache grew correctly across requests")
        return True
    except AssertionError as e:
        _fail("history accumulation", str(e))
        return False
    except Exception as e:
        _fail("history accumulation", str(e))
        return False


def test_user_isolation() -> bool:
    """Each UID has its own independent history slot."""
    uid_a = "isolation-a"
    uid_b = "isolation-b"
    clear_history(uid_a)
    clear_history(uid_b)
    try:
        post("Mensagem do usuário A.", uid=uid_a)
        post("Mensagem do usuário B.", uid=uid_b)

        hist_a = get_history(uid_a)
        hist_b = get_history(uid_b)

        assert hist_a["count"] == 2, f"uid_a expected 2 entries, got {hist_a['count']}"
        assert hist_b["count"] == 2, f"uid_b expected 2 entries, got {hist_b['count']}"

        # Histories must not share entries
        assert hist_a["history"] != hist_b["history"], "uid_a and uid_b share history!"

        _ok("user isolation — each UID has its own independent cache slot")
        return True
    except AssertionError as e:
        _fail("user isolation", str(e))
        return False
    except Exception as e:
        _fail("user isolation", str(e))
        return False


def test_trim_to_40() -> bool:
    """History is trimmed to 40 entries after exceeding the limit."""
    uid = "trim-test"
    clear_history(uid)
    try:
        # Send 21 messages — that's 42 entries, which exceeds the 40-entry cap
        for i in range(21):
            post(f"Mensagem {i}.", uid=uid)

        hist = get_history(uid)
        assert hist["count"] == 40, (
            f"expected 40 entries after trimming, got {hist['count']}"
        )

        _ok("trim — history capped at 40 entries after 21 requests")
        return True
    except AssertionError as e:
        _fail("trim", str(e))
        return False
    except Exception as e:
        _fail("trim", str(e))
        return False


def set_server_ttl(ttl: int) -> None:
    resp = requests.post(f"{HOST}/debug/set-ttl", params={"ttl": ttl}, timeout=5)
    resp.raise_for_status()


def test_ttl_expiry(ttl_seconds: int = 5) -> bool:
    """After TTL elapses, the cache entry is gone.

    Swaps the module-level cache for one with a short TTL via the debug endpoint,
    then restores it after the test.
    """
    uid = "ttl-test"
    try:
        set_server_ttl(ttl_seconds)
        clear_history(uid)

        post("Mensagem antes do TTL expirar.", uid=uid)

        after_1 = get_history(uid)
        assert after_1["count"] == 2, (
            f"expected 2 entries before TTL, got {after_1['count']}"
        )

        wait = ttl_seconds + 2
        print(f"  [INFO] Sleeping {wait}s for TTL={ttl_seconds}s to expire …")
        time.sleep(wait)

        after_ttl = get_history(uid)
        assert after_ttl["count"] == 0, (
            f"expected 0 entries after TTL expiry, got {after_ttl['count']}"
        )

        _ok(f"TTL expiry — history cleared after {ttl_seconds}s TTL elapsed")
        return True
    except AssertionError as e:
        _fail("TTL expiry", str(e))
        return False
    except Exception as e:
        _fail("TTL expiry", str(e))
        return False
    finally:
        set_server_ttl(1200)  # restore production TTL


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    include_ttl = "--ttl" in sys.argv

    print("Starting minimal test server (tests.test_server:app) …")
    env = os.environ.copy()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "tests.test_server:app",
            "--port",
            "8787",
            "--log-level",
            "warning",
        ],
        env=env,
    )

    try:
        if not wait_for_server():
            print("[ERROR] Server did not become ready within 20 seconds.")
            proc.terminate()
            sys.exit(1)

        print("Server ready.\n")

        results = [
            test_cache_type(),
            test_connectivity(),
            test_history_accumulation(),
            test_user_isolation(),
        ]

        if include_ttl:
            print()
            print("Running TTL expiry test (server must have ttl=5 in chat.py) …")
            results.append(test_ttl_expiry(ttl_seconds=5))
        else:
            print()
            print(
                "  [SKIP] TTL expiry test — run with --ttl after setting ttl=5 in chat.py"
            )

    finally:
        proc.terminate()
        proc.wait()

    failures = results.count(False)
    print()
    if failures == 0:
        print("All tests passed.")
        sys.exit(0)
    else:
        print(f"{failures} test(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
