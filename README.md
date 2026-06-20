# Aegis — Encrypted Secrets Manager

A CLI tool to store, retrieve, and manage encrypted secrets.  
**No cloud. No account. Just encryption.**

```
    ___              _
   /   | ___  ____ _(_)____
  / /| |/ _ \/ __ `/ / ___/
 / ___ /  __/ /_/ / (__  )
/_/  |_\___/\__, /_/____/
           /____/

Aegis v1.0.0 • Encrypted Secrets Manager
```

## Quick Start

```bash
aegis setup              # Create vault (first time)
aegis auth               # Authenticate (30-min session)
aegis save github-token password   # Save a secret
aegis show github-token  # Retrieve & auto-copy
aegis list               # List all secrets
aegis lock               # Lock vault
```

## Commands

| Command | Description |
|---------|-------------|
| `aegis setup` | Initialize vault with master password |
| `aegis auth` | Authenticate (30-min session) |
| `aegis save <name> <tag>` | Save secret with a tag (password, api, env, etc.) |
| `aegis show <name>` | Retrieve secret and copy to clipboard |
| `aegis list [tag]` | List all secrets or filter by tag |
| `aegis delete <name>` | Delete a secret |
| `aegis find <query>` | Search secrets by name |
| `aegis generate [length]` | Generate a random password |
| `aegis lock` | Lock vault and end session |

## Examples

```bash
# Save with any tag you want
aegis save github-token password
aegis save prod-db-url database
aegis save stripe-key api
aegis save OPENAI_KEY env

# List all or filter by tag
aegis list
aegis list password

# Retrieve (auto-copies to clipboard)
aegis show github-token

# Search
aegis find stripe

# Generate a password
aegis generate
aegis generate 16
```

## Security

- **AES-256-GCM** — authenticated encryption per secret
- **Argon2id** — memory-hard key derivation
- **Session-based** — 30-min timeout, keys in memory only
- **Clipboard auto-clear** — secrets removed after 30s
- **Rate limiting** — 3 failed attempts = 5-min lockout
- **Local only** — vault is a file in `~/.aegis/`

## Installation

```bash
git clone https://github.com/afzanlearns/Aegis.git
cd aegis
pip install -e .
```

Requires Python 3.10+.

## License

MIT
