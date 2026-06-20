# Aegis — Encrypted Secrets Manager

> **Guardian of Your Credentials**  
> *Military-grade encrypted secrets manager for developers — AES-256-GCM, Argon2id, zero cloud.*

Aegis is a secure, minimal credential manager that lets developers store and retrieve passwords, API keys, and secrets from the command line. **No cloud, no account, no friction** — just encryption at rest and in transit.

```
    _    ____  ___    _     _____
   / \  |  _ \/ _ \  / |   / ____|
  / _ \ | |_) | | | | |   | (___
 / ___ \|  _ <| |_| | |    \___ \
/_/   \_\_| \_\\___/  |_|    ____) |
                                  |___/

  Aegis v1.0.0 • Encrypted Secrets Manager
  "Guardian of Your Credentials"
```

---

## Table of Contents

- [Features](#features)
- [Security Architecture](#security-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Design & UI](#design--ui)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Daily Workflow](#daily-workflow)
- [Backup & Recovery](#backup--recovery)
- [Security Checklist](#security-checklist)
- [Development](#development)
- [Future Enhancements](#future-enhancements)
- [Compliance & Security Notes](#compliance--security-notes)
- [License](#license)

---

## Features

### Core Security

| Feature | Detail |
|---------|--------|
| **AES-256-GCM** | Authenticated encryption with random IV per secret |
| **Argon2id KDF** | Memory-hard, GPU-resistant key derivation |
| **Session-based access** | 30-minute timeout, keys exist only in memory |
| **Rate limiting** | 3 failed attempts = 5-minute lockout |
| **Zero plaintext storage** | Secrets always encrypted at rest |
| **Constant-time comparison** | Timing-attack resistant password verification |

### Developer Experience

| Feature | Detail |
|---------|--------|
| **12 CLI commands** | `auth`, `save`, `get`, `list`, `search`, `delete`, `generate`, `export`, `import`, `audit`, `logout`, `setup` |
| **Clipboard auto-clear** | Secrets removed from clipboard after 30 seconds |
| **Audit logging** | Append-only log of every operation |
| **Password generation** | Cryptographically secure, customizable length & symbols |
| **Encrypted backups** | Export/import with optional password layer |
| **Beautiful terminal UI** | Purple/gold theme with Rich-powered panels |

---

## Security Architecture

```
Master Password
      │
      ▼
  Argon2id KDF  ──► Encryption Key (256-bit)
      │
      ├──► AES-256-GCM Encrypt/Decrypt
      │
      ▼
  PBKDF2-SHA256 ──► Password Hash (verification only)
      │
      ▼
  Session Token (30-min expiry, memory-only)
```

### Key Security Properties

- **Master password is never stored** — only the PBKDF2-SHA256 hash is persisted
- **Encryption key is derived fresh each session** — never written to disk after logout
- **Random IV per encryption** — prevents pattern analysis across secrets
- **Authenticated encryption (GCM)** — detects tampering and corruption
- **Constant-time comparison** — prevents timing side-channel attacks
- **Rate limiting** — 3 consecutive failed authentication attempts trigger a 5-minute lockout
- **File permissions** — vault directory `0o700`, vault files `0o600` (owner-only on POSIX)
- **Secure memory handling** — sensitive data overwritten with zeroes via `ctypes`

### Cryptographic Standards

| Algorithm | Purpose | Standard |
|-----------|---------|----------|
| AES-256-GCM | Secret encryption/decryption | NIST SP 800-38D |
| Argon2id | Key derivation (memory-hard) | RFC 9106 / PHC winner |
| PBKDF2-HMAC-SHA256 | Password verification only | RFC 2898 |
| `os.urandom` | Cryptographic randomness | NIST SP 800-90A |

---

## Installation

### From Source

```bash
git clone https://github.com/afzanlearns/Aegis.git
cd aegis
pip install -e .
```

### Via PyPI (when published)

```bash
pip install aegis-secrets
```

### System Requirements

- Python 3.10+
- Windows, macOS, or Linux

---

## Quick Start

### First-Time Setup

```bash
# Create your vault with a master password (12+ characters)
aegis setup
```

You'll be prompted to create a master password. This is the **only** password you'll need to remember — it unlocks your entire vault.

### Authenticate

```bash
# Start a 30-minute authenticated session
aegis auth
```

### Save a Secret

```bash
# Provide the value inline
aegis save github-token ghp_xxxxxxxxxxxx

# Or enter it securely (hidden prompt)
aegis save prod-db-password --password
```

### Retrieve a Secret

```bash
# Display in terminal
aegis get github-token

# Copy to clipboard (clears automatically in 30 seconds)
aegis get github-token --copy
```

### List & Search

```bash
# List all stored secrets (values redacted)
aegis list

# Search by name
aegis search database
```

### Generate a Password

```bash
# Generate a 32-character password with symbols
aegis generate --length 32

# Generate and save directly
aegis generate --length 40 --no-symbols --save my-new-key
```

### View Audit Log

```bash
# See who accessed what and when
aegis audit

# Limit to recent entries
aegis audit --limit 10
```

### End Session

```bash
# Lock the vault and clear session
aegis logout
```

---

## Command Reference

| Command | Description |
|---------|-------------|
| `aegis setup` | Initialize vault with master password (first use only) |
| `aegis auth` | Authenticate and start a 30-minute session |
| `aegis save <name>` | Save an encrypted secret (use `--password` for hidden prompt, `--type` for categorization) |
| `aegis get <name>` | Retrieve and decrypt a secret (`--copy` copies to clipboard with auto-clear) |
| `aegis list` | List all stored secrets (values hidden, metadata shown) |
| `aegis search <query>` | Search secrets by name |
| `aegis delete <name>` | Delete a secret (with confirmation prompt; use `--force` to skip) |
| `aegis generate` | Generate a cryptographically secure password (`--length`, `--no-symbols`, `--save`) |
| `aegis export` | Export encrypted backup (`--path`, `--password` for extra encryption layer) |
| `aegis import <path>` | Import secrets from backup file (`--password` if backup is encrypted) |
| `aegis audit` | View audit log (`--limit N` to control entries shown) |
| `aegis logout` | End session and lock vault |

### Secret Types

When saving secrets, you can categorize them with `--type` (or `-t`):

| Type | Description |
|------|-------------|
| `password` | General password (default) |
| `api-key` | API key or token |
| `duo` | Pair of credentials (access key + secret key) |
| `url` | URL with embedded credentials |
| `secret` | Generic sensitive string |

---

## Design & UI

### Color Palette

Aegis features a distinctive purple and gold theme inspired by premium security tools.

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#9C27B0` | Headers, highlights, border accents |
| Secondary | `#BA68C8` | Secondary UI accents |
| Accent | `#D39CE0` | Subtle borders, decorative elements |
| Gold | `#FFD700` | Premium accents, vault icons, tips |
| Success | `#4CAF50` | Authentication success, confirmations |
| Error | `#FF5252` | Failed operations, denied access |
| Warning | `#FFC107` | Cautions, confirmations |
| Text | `#FFFFFF` | Primary content |
| Muted | `#808080` | Secondary labels, metadata |

### UI Layouts

**Vault status:**
```
┌─ aegis • vault ─────────────────────────────────────────┐
│                                                          │
│  ✓ Authenticated (expires in 28m 45s)                   │
│                                                          │
│  Stored Secrets:  8 items                                │
│  Initialized: 2025-06-15T10:30:00                        │
│                                                          │
│  Run 'aegis --help' for available commands               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Secrets list:**
```
┌─ aegis • list ───────────────────────────────────────────┐
│                                                          │
│  🔐 Your Secrets (5 stored)                              │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │ Name              │ Type       │ Created        │     │
│  ├─────────────────────────────────────────────────┤     │
│  │ github-token      │ API Key    │ 2d ago         │     │
│  │ prod-db-password  │ Password   │ 3w ago         │     │
│  │ aws-keys          │ Duo        │ 1m ago         │     │
│  │ stripe-api-key    │ API Key    │ 2w ago         │     │
│  │ jwt-secret        │ Secret     │ today          │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  💡 Tip: aegis get <name> --copy                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Clipboard copy confirmation:**
```
┌─ aegis • get github-token ───────────────────────────────┐
│                                                          │
│  ✓ Retrieved 'github-token'                              │
│  📋 Copied to clipboard (clears in 30s)                  │
│                                                          │
│  💡 Value will auto-clear from clipboard for security    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
aegis/
├── src/
│   ├── __init__.py
│   ├── exceptions.py                  # Custom exception hierarchy
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                    # Click entry point, command registration
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── setup.py               # aegis setup
│   │   │   ├── auth.py                # aegis auth
│   │   │   ├── save.py                # aegis save
│   │   │   ├── get.py                 # aegis get
│   │   │   ├── list.py                # aegis list
│   │   │   ├── search.py              # aegis search
│   │   │   ├── delete.py              # aegis delete
│   │   │   ├── generate.py            # aegis generate
│   │   │   ├── export.py              # aegis export
│   │   │   ├── import_cmd.py          # aegis import
│   │   │   ├── audit.py               # aegis audit
│   │   │   └── logout.py              # aegis logout
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── output.py              # Rich terminal formatting (purple/gold theme)
│   │       └── password_strength.py   # Password strength evaluation
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── crypto.py                  # AES-256-GCM encrypt/decrypt
│   │   ├── key_derivation.py           # Argon2id + PBKDF2
│   │   ├── session.py                 # Session management with timeout
│   │   ├── config.py                  # Vault config persistence
│   │   ├── models.py                  # Data models
│   │   └── vault.py                   # Central orchestrator
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── clipboard.py               # Secure clipboard with auto-clear timer
│   │   ├── memory.py                  # Memory wiping via ctypes/libc
│   │   └── permissions.py             # File permission enforcement
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py                # SQLite wrapper (secrets CRUD)
│   │   └── audit_log.py              # Append-only audit logger
│   │
│   └── utils/
│       └── __init__.py
│
├── tests/
│   ├── __init__.py
│   ├── test_crypto.py                 # AES-256-GCM roundtrip, tamper detection
│   ├── test_key_derivation.py          # Argon2id determinism, PBKDF2 verification
│   ├── test_session.py                # Session create/validate/expire/destroy
│   └── test_storage.py               # SQLite CRUD, search, bulk import
│
├── examples/
│   ├── audit-log-example.txt          # Sample audit log format
│   └── example-export.json           # Sample exported backup
│
├── requirements.txt                   # click, rich, cryptography, pyperclip
├── setup.py                           # Package configuration
└── README.md                          # This file
```

---

## Core Components

### Encryption Layer (`src/core/crypto.py`)

Uses `cryptography` library's `AESGCM` implementation — NIST-approved AES-256 in Galois/Counter mode. Every encryption generates a fresh 96-bit random nonce. The 128-bit authentication tag is stored alongside the ciphertext, ensuring any tampering or key mismatch is detected on decryption.

### Key Derivation (`src/core/key_derivation.py`)

Two separate key derivation functions serve distinct purposes:

1. **Argon2id** — Derives the 256-bit encryption key from the master password. Configured with 64 MB memory cost, 2 iterations, and 8 lanes. This is the **primary defense** against GPU/ASIC-based brute force.

2. **PBKDF2-HMAC-SHA256** — Creates the verification hash stored in `config.json`. This hash is used **only** for verifying the master password on login, not for encryption. This separation ensures that even if the config file is compromised, the encryption key cannot be recovered.

### Session Management (`src/core/session.py`)

Sessions are stored in `.session` within the vault directory with `0o600` permissions. The session file contains:
- `authenticated_at` — When the session was created
- `expires_at` — When the session expires (default: 30 minutes)
- `key` — The derived encryption key (hex-encoded)

On logout, the session file is deleted and the key is destroyed. Expired sessions are automatically invalidated and cleaned up.

### Central Vault (`src/core/vault.py`)

The `VaultManager` class orchestrates all operations:
- Routes CLI requests to the appropriate security, storage, and audit components
- Manages rate limiting via a `.lockout` file (3 failed auth attempts = 5-minute lockout)
- Handles encrypted backup export/import with an optional password layer
- Generates cryptographically secure passwords using `os.urandom`

### Audit Logging (`src/storage/audit_log.py`)

All vault operations are logged to an append-only audit table in the SQLite database. Each entry records:
- **Action** — The operation performed (`auth_success`, `save_secret`, `get_secret`, etc.)
- **Secret name** — Which secret was accessed (or `null` for auth events)
- **Timestamp** — When the event occurred
- **Success** — Whether the operation succeeded
- **Details** — Additional context (e.g., "Decryption failed", "8 secrets exported")

---

## Daily Workflow

```bash
# Start of day
aegis auth
✓ Authenticated (30 min session)

# Save credentials as you use them
aegis save github-token ghp_xxx
✓ Saved 'github-token'

aegis save prod-db --password
Value: ••••••••••
✓ Saved 'prod-db'

# Retrieve when needed (auto-clears from clipboard)
aegis get github-token --copy
✓ Copied (clears in 30s)

# Check what you have
aegis list
┌─ Name               │ Type       │ Created     ─┐
│ github-token        │ API Key    │ 2d ago       │
│ prod-db             │ Password   │ 1h ago       │
└─────────────────────────────────────────────────┘

# End of day
aegis logout
✓ Session ended
```

---

## Backup & Recovery

### Export

```bash
# Standard export (secrets are decrypted in the backup)
aegis export --path ~/backups/aegis-backup.json

# Password-protected export (extra encryption layer)
aegis export --path ~/backups/aegis-backup.enc --password
```

> **Warning:** Without `--password`, the backup file contains plaintext secrets. Store it securely.

### Import

```bash
# Import from standard backup
aegis import ~/backups/aegis-backup.json

# Import from password-protected backup
aegis import ~/backups/aegis-backup.enc --password
```

---

## Security Checklist

### Critical

- [x] Master password is **never stored** — only the PBKDF2-SHA256 hash is persisted
- [x] Encryption key is **derived fresh each session** — never stored on disk after logout
- [x] AES-256-GCM with **random IV per secret** — prevents pattern analysis
- [x] **HMAC authentication** (GCM tag) — detects tampering and corruption
- [x] Session key cleared on logout — session file deleted
- [x] Clipboard auto-clear after 30 seconds — timer-based secure clearing
- [x] File permissions: `0o600` for vault files, `0o700` for vault directory (POSIX)
- [x] Rate limiting — 3 failed auth attempts = 5-minute lockout
- [x] Audit log is append-only — operations are recorded immutably

### Important

- [x] Argon2id with **64 MB memory cost** — GPU and ASIC resistant
- [x] **Constant-time** password comparison via `hmac.compare_digest`
- [x] Secure random number generation via `os.urandom`
- [x] No plaintext secrets in logs, error messages, or memory dumps
- [x] Proper exception handling — no information leakage in error messages
- [x] Session timeout enforced — 30-minute default, automatically expires
- [x] Memory wiping for sensitive data — `ctypes`-based zero overwrite

---

## Development

### Setup

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_crypto.py -v

# With coverage
pytest tests/ --cov=src -v
```

### Test Coverage

| Test File | What It Validates |
|-----------|------------------|
| `test_crypto.py` | AES-256-GCM roundtrip, wrong key/nonce rejection, empty input, special characters, IV uniqueness, key size validation |
| `test_key_derivation.py` | Argon2id key derivation, deterministic with same salt, PBKDF2 hash/verify, wrong password/salt rejection, constant-time comparison timing |
| `test_session.py` | Session creation, validation, expiry, destroy, custom timeout, edge cases with missing session |
| `test_storage.py` | SQLite CRUD operations, secret search, bulk import, entry count, error handling for missing/duplicate secrets |

### Code Style

- Python 3.10+ type hints throughout
- `snake_case` for functions and variables
- `PascalCase` for classes
- Comprehensive error handling with custom exception hierarchy
- Docstrings on all public methods

---

## Future Enhancements

- [ ] **REST API** — Local HTTP API for integration with other tools
- [ ] **Browser extension** — Autofill forms directly from vault
- [ ] **Encrypted sync** — End-to-end encrypted synchronization across devices
- [ ] **Two-factor authentication** — TOTP or hardware key support
- [ ] **Hardware key integration** — YubiKey for master password replacement
- [ ] **Biometric unlock** — Fingerprint or face recognition (OS integration)
- [ ] **Mobile companion** — Read-only access from phone
- [ ] **Team sharing** — Encrypted secret sharing between team members
- [ ] **Web dashboard** — Optional browser-based UI
- [ ] **Password health audit** — Weak, reused, or compromised password detection

---

## Compliance & Security Notes

### Threat Model

Aegis protects secrets in the following scenarios:
- **At rest:** Secrets are encrypted in SQLite using AES-256-GCM. The vault directory has restrictive file permissions.
- **In use:** Decrypted secrets exist only in the authenticated session's memory. The clipboard is cleared after 30 seconds.
- **In transit:** Backup files can be password-encrypted. Future sync features will use end-to-end encryption.

### Out of Scope (by design)

- **Lost master password recovery** — There is no backdoor. If you forget your master password, your secrets are unrecoverable. This is a security feature, not a bug.
- **Multi-device sync** — Vault files are local. Sync will be added as an optional future feature with end-to-end encryption.
- **Zero-knowledge proof** — Possible future enhancement but not implemented in v1.0.

### Recommendations

- **Master password:** Use 16+ characters with mixed case, numbers, and symbols
- **Session timeout:** Default 30 minutes; adjust if needed (see `config.json`)
- **Backup frequency:** Weekly encrypted exports
- **Audit log review:** Monthly review of access patterns

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with integrity. Secured with cryptography. Designed for developers.*
