# Aegis — Encrypted Secrets Manager

```
   ░███                          ░██
  ░██░██                     ░██
 ░██  ░██   ░███████   ░████████ ░██ ░███████
░█████████ ░██    ░██ ░██    ░██ ░██░██
░██    ░██ ░█████████ ░██    ░██ ░██ ░███████
░██    ░██ ░██        ░██   ░███ ░██       ░██
░██    ░██  ░███████   ░█████░██ ░██ ░███████
                             ░██
                       ░███████
```

A CLI tool to store, retrieve, and manage encrypted secrets.  
**No cloud. No account. Just encryption.**

Every secret is encrypted with **AES-256-GCM** and unlocked with a single master password. Your vault lives in `~/.aegis/` — fully local, fully under your control.

---

## Features

| Area | Detail |
|------|--------|
| **AES-256-GCM** | Authenticated encryption — each secret gets a unique random nonce |
| **Argon2id KDF** | Memory-hard, GPU-resistant key derivation (64 MB, 2 iterations, 8 lanes) |
| **User-defined tags** | Categorize secrets however you want — `password`, `api`, `env`, `database`, `token` |
| **Clipboard auto-clear** | Secrets removed from clipboard after 30 seconds |
| **Session-based access** | 30-minute session timeout, encryption key never persisted after logout |
| **Rate limiting** | 3 failed auth attempts = 5-minute lockout |
| **Password generation** | Cryptographically secure with full symbol set |
| **No cloud** | Vault is a local SQLite database at `~/.aegis/secrets.db` |

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

### What gets stored

| File | Contents | Permissions |
|------|----------|-------------|
| `~/.aegis/config.json` | Argon2 salt, PBKDF2 password hash | `600` (owner rw) |
| `~/.aegis/secrets.db` | Encrypted secrets + audit log | `600` (owner rw) |
| `~/.aegis/.session` | Derived encryption key (30-min expiry) | `600` (owner rw) |
| `~/.aegis/.lockout` | Failed attempt counter | `600` (owner rw) |

### What is never stored

- Your **master password** — only the Argon2-derived key and PBKDF2 hash exist on disk
- The **encryption key** after logout — the session file is deleted
- **Plaintext secrets** — always encrypted at rest with AES-256-GCM

---

## Installation

### From Source

```bash
git clone https://github.com/afzanlearns/Aegis.git
cd aegis
pip install -e .
```

### Requirements

- Python 3.10+
- Windows, macOS, or Linux

---

## Quick Start

```bash
# 1. Create your vault
aegis setup

# 2. Authenticate
aegis auth

# 3. Save secrets
aegis save github-token password
aegis save prod-db-url database
aegis save stripe-key api

# 4. List what you have
aegis list

# 5. Retrieve a secret (auto-copies to clipboard)
aegis show github-token

# 6. Lock when done
aegis lock
```

---

## Command Reference

### `aegis setup`

Initialize the vault with a master password (first use only).

```bash
aegis setup
```

You'll be prompted to create and confirm a master password (12+ characters with mixed case, numbers, and symbols).

---

### `aegis auth`

Authenticate and start a 30-minute session. Every vault command requires an active session.

```bash
aegis auth
```

Sessions are enforced at the command level — running `aegis save`, `aegis show`, `aegis list`, `aegis delete`, `aegis find`, or `aegis generate --save` without an active session will fail with:

```
[ERR] Not authenticated
Run 'aegis auth' to authenticate
```

---

### `aegis save <name> <tag>`

Save a secret with a user-defined tag. Tags are completely free-form — use whatever makes sense for your workflow.

```bash
aegis save github-token password
Value: ghp_xxxxxxxxxxxxxxxxxxxx
[OK] Saved 'github-token' [password]
```

**Tags are whatever you want:**

```bash
aegis save prod-db-url   database
aegis save stripe-key    api
aegis save OPENAI_KEY    env
aegis save aws-access    token
aegis save ssh-key       key
aegis save wifi-code     network
```

The value is always prompted with hidden input — no flags needed.

---

### `aegis show <name>`

Retrieve a secret and automatically copy it to the clipboard. The clipboard is cleared after 30 seconds.

```bash
aegis show github-token
[OK] Retrieved 'github-token'
[COPY] Copied to clipboard (clears in 30s)
```

No `--copy` flag needed — it always copies.

---

### `aegis list [tag]`

List all stored secrets, or filter by a specific tag.

```bash
# All secrets
aegis list
Your Secrets (3 stored)

Name              Tag         Created
────────────────────────────────────
github-token      password    just now
prod-db-url       database    1m ago
stripe-key        api         2m ago

# Filter by tag
aegis list password
Passwords (1 stored)

Name              Created
───────────────────────
github-token      just now
```

---

### `aegis delete <name>`

Delete a secret. Confirmation is required.

```bash
aegis delete stripe-key
Delete 'stripe-key'? [y/N]: y
[OK] Deleted 'stripe-key'
```

---

### `aegis find <query>`

Search secrets by name.

```bash
aegis find github
Found 1 secret

Name              Tag         Created
─────────────────────────────────────
github-token      password    2d ago
```

---

### `aegis generate [length]`

Generate a cryptographically secure random password. Default length is 32 characters with full symbols.

```bash
aegis generate
kX9$mL2@pQ7*nB4#wZ8&vJ1%sH6!tY3^

aegis generate 16
dK7#mP9$vL2@nQ4&
```

---

### `aegis lock`

End the current session and lock the vault. The encryption key is destroyed.

```bash
aegis lock
[OK] Vault locked
```

---

## Tags

Tags replace traditional secret types. Instead of choosing from a fixed list (`password`, `api-key`, `duo`, `url`, `secret`), you use any string that describes the secret's purpose.

```bash
aegis save my-token password
aegis save db-url    database
aegis save api-key   api
aegis save env-var   env
```

Filter by tag:

```bash
aegis list api
aegis list database
aegis list env
```

This makes organization flexible — you define the taxonomy.

---

## Session & Authentication

Every vault-modifying command requires authentication. The session lasts 30 minutes by default and is enforced at two levels:

1. **Command-level check** — Each command calls `VaultManager.is_authenticated()` before any operation
2. **Vault-layer check** — Every vault method calls `_require_auth()` as defense in depth

```bash
# Fails without auth
aegis show my-secret
[ERR] Not authenticated
Run 'aegis auth' to authenticate

# Succeeds after auth
aegis auth
Master Password: ••••••••••
[OK] Authenticated
[*] Session expires in 30 minutes
```

Commands that do not require authentication:

- `aegis setup` — First-time initialization
- `aegis auth` — Authentication itself
- `aegis lock` — Ending a session
- `aegis generate` — Password generation (no vault access)

---

## Project Structure

```
src/
├── exceptions.py                  # Custom exception hierarchy
├── cli/
│   ├── main.py                    # Click entry point, command registration
│   └── commands/
│       ├── setup.py               # aegis setup
│       ├── auth.py                # aegis auth
│       ├── save.py                # aegis save <name> <tag>
│       ├── show.py                # aegis show <name>
│       ├── list.py                # aegis list [tag]
│       ├── delete.py              # aegis delete <name>
│       ├── find.py                # aegis find <query>
│       ├── generate.py            # aegis generate [length]
│       └── lock.py                # aegis lock
│   └── utils/
│       ├── output.py              # Rich terminal formatting
│       └── password_strength.py   # Strength evaluation
├── core/
│   ├── crypto.py                  # AES-256-GCM encrypt/decrypt
│   ├── key_derivation.py          # Argon2id + PBKDF2
│   ├── session.py                 # Session management with timeout
│   ├── config.py                  # Vault config persistence
│   ├── models.py                  # Data models (SecretEntry, AuditEntry)
│   └── vault.py                   # Central orchestrator
├── security/
│   ├── clipboard.py               # Secure clipboard with auto-clear
│   ├── memory.py                  # Memory wiping via ctypes
│   └── permissions.py             # File permission enforcement
├── storage/
│   ├── database.py                # SQLite wrapper (secrets CRUD)
│   └── audit_log.py               # Append-only audit logger
└── utils/
    └── __init__.py
```

---

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v
```

All internal APIs are public and documented with type hints.

---

## License

MIT
