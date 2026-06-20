# Aegis — Encrypted Secrets Manager

**Guardian of Your Credentials**

Aegis is a secure, minimal credential manager for developers. Store and retrieve passwords, API keys, and secrets from the command line. No cloud, no account, no friction—just encryption at rest.

## Features

- **AES-256-GCM** authenticated encryption for all secrets
- **Argon2id** key derivation (memory-hard, GPU-resistant)
- **Session-based access** with 30-minute timeout
- **Audit logging** for all operations
- **Clipboard auto-clear** after 30 seconds
- **Rate limiting** after 3 failed authentication attempts
- **Zero plaintext storage** — secrets are always encrypted
- **Secure memory handling** with memory wipe utilities
- **File permission enforcement** (0o600 for sensitive files)
- **Beautiful terminal UI** with purple/gold theme

## Installation

```bash
# Install from source
cd aegis
pip install -e .

# Or install directly
pip install aegis-secrets
```

## Quick Start

```bash
# First-time setup
aegis setup

# Authenticate (30-minute session)
aegis auth

# Save a secret
aegis save github-token ghp_xxxxxxxxxxxx

# Retrieve a secret
aegis get github-token

# Copy to clipboard (clears in 30s)
aegis get github-token --copy

# List all secrets
aegis list

# Search secrets
aegis search database

# Generate a strong password
aegis generate --length 32

# Delete a secret
aegis delete old-key

# View audit log
aegis audit

# Lock the vault
aegis logout
```

## Commands

| Command | Description |
|---------|-------------|
| `aegis setup` | Initialize vault with master password (first use) |
| `aegis auth` | Authenticate and start a 30-minute session |
| `aegis save <name> [--value]` | Save an encrypted secret |
| `aegis get <name> [--copy]` | Retrieve and decrypt a secret |
| `aegis list` | List all stored secrets (values hidden) |
| `aegis search <query>` | Search secrets by name |
| `aegis delete <name>` | Delete a secret |
| `aegis generate [--length N]` | Generate a strong password |
| `aegis export [--path] [--password]` | Export encrypted backup |
| `aegis import <path> [--password]` | Import secrets from backup |
| `aegis audit [--limit N]` | View audit log |
| `aegis logout` | End session and lock vault |

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
  Session Token (30-min expiry)
```

### Key Security Properties

- **Master password is never stored** — only the PBKDF2 hash is persisted
- **Encryption key is derived fresh each session** — never written to disk after session ends
- **Random IV per encryption** — prevents pattern analysis
- **Authenticated encryption** (GCM) — detects tampering
- **Constant-time comparison** — prevents timing attacks
- **Rate limiting** — 3 failed attempts = 5-minute lockout
- **File permissions** — vault files restricted to owner only (0o600/0o700)

## Project Structure

```
src/
├── cli/              # CLI commands and UI
│   ├── commands/     # aegis setup, auth, save, get, etc.
│   ├── utils/        # Rich output formatting, password strength
│   └── main.py       # Entry point
├── core/             # Core security engine
│   ├── crypto.py     # AES-256-GCM encryption
│   ├── key_derivation.py  # Argon2id + PBKDF2
│   ├── session.py    # Session management
│   ├── config.py     # Vault configuration
│   ├── models.py     # Data models
│   └── vault.py      # Main vault orchestrator
├── security/         # Security utilities
│   ├── clipboard.py  # Secure clipboard with auto-clear
│   ├── memory.py     # Memory wiping utilities
│   └── permissions.py # File permission enforcement
├── storage/          # Storage layer
│   ├── database.py   # SQLite wrapper
│   └── audit_log.py  # Audit logging
├── utils/            # Shared utilities
└── exceptions.py     # Custom exception classes
```

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Or run the test suite directly
python test_e2e.py
```

## Security Considerations

- **Lost master password = lost secrets.** There is no recovery mechanism by design.
- **Vault files are local** — stored in `~/.aegis/` with restricted permissions.
- **Session keys exist only in memory** and are destroyed on logout.
- **Clipboard secrets auto-clear** after 30 seconds to prevent exposure.

## License

MIT
