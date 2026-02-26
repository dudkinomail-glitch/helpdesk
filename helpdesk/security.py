from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta


PBKDF2_ITERATIONS = 180_000


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${key.hex()}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt_hex, key_hex = encoded_hash.split("$", maxsplit=3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
    except (ValueError, TypeError):
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected_key)


@dataclass
class LoginAttemptState:
    failed_attempts: int = 0
    blocked_until: datetime | None = None


@dataclass
class BruteForceProtector:
    max_attempts: int = 5
    block_minutes: int = 15
    states: dict[str, LoginAttemptState] = field(default_factory=dict)

    def is_blocked(self, identity: str, now: datetime | None = None) -> bool:
        now = now or datetime.utcnow()
        state = self.states.get(identity)
        if not state or not state.blocked_until:
            return False
        if state.blocked_until <= now:
            state.blocked_until = None
            state.failed_attempts = 0
            return False
        return True

    def register_failure(self, identity: str, now: datetime | None = None) -> None:
        now = now or datetime.utcnow()
        state = self.states.setdefault(identity, LoginAttemptState())
        state.failed_attempts += 1
        if state.failed_attempts >= self.max_attempts:
            state.blocked_until = now + timedelta(minutes=self.block_minutes)

    def register_success(self, identity: str) -> None:
        state = self.states.setdefault(identity, LoginAttemptState())
        state.failed_attempts = 0
        state.blocked_until = None
