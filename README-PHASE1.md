# BramTech VTU — Phase 1: Ledger Foundation

This is the beating heart of the platform. Three apps:

- **`apps.accounts`** — Custom User with phone-first login, KYC tiers, reseller tiers, transaction PIN
- **`apps.ledger`** — Immutable double-entry accounting (Account, Journal, LedgerEntry) + `LedgerService`
- **`apps.wallets`** — Race-safe wallet operations with `SELECT FOR UPDATE` + `WalletService`

## What's in this zip

```
src/
├── apps/
│   ├── __init__.py                          NEW
│   ├── accounts/                            NEW ENTIRE APP
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── admin.py
│   │   ├── managers.py
│   │   ├── models.py
│   │   ├── migrations/__init__.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_user_model.py
│   ├── ledger/                              NEW ENTIRE APP
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── migrations/__init__.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_ledger_service.py
│   └── wallets/                             NEW ENTIRE APP
│       ├── __init__.py
│       ├── apps.py
│       ├── admin.py
│       ├── models.py
│       ├── services.py
│       ├── signals.py
│       ├── migrations/__init__.py
│       └── tests/
│           ├── __init__.py
│           └── test_wallet_service.py
└── config/
    └── settings/
        └── base.py                          REPLACES existing base.py

pytest.ini                                    NEW (in project root)
```

## How to install

### 1. Backup your existing custom user (safety net)

You already created a superuser `BRIGHTO25` in the default `auth.User` table.
Since we're **switching** to a custom User model, the existing superuser
will become invalid. That's fine for dev — we'll just create a new one.

**Important:** Because you already have `auth.User` migrations applied,
the switch to a custom user model requires a **fresh database**.

### 2. Extract this zip into your project root

Unzip and let the files land under `~/projects/bramtech-vtu/`. Your VS Code
will show new files highlighted; the only overwrite is `src/config/settings/base.py`.

### 3. Stop docker and wipe the database (dev only!)

```bash
docker compose down -v
```

The `-v` flag wipes the postgres volume. Safe here because we have no real
data yet.

### 4. Rebuild and start fresh

```bash
docker compose up -d postgres redis
```

Wait ~10 seconds for Postgres to be ready.

### 5. Create migrations for the new apps

```bash
docker compose run --rm django python manage.py makemigrations accounts ledger wallets
```

You should see output like:
```
Migrations for 'accounts':
  apps/accounts/migrations/0001_initial.py
    - Create model User
Migrations for 'ledger':
  apps/ledger/migrations/0001_initial.py
    - Create model Account
    - Create model Journal
    - Create model LedgerEntry
Migrations for 'wallets':
  apps/wallets/migrations/0001_initial.py
    - Create model Wallet
```

### 6. Apply all migrations

```bash
docker compose run --rm django python manage.py migrate
```

### 7. Create a new superuser

```bash
docker compose run --rm django python manage.py createsuperuser
```

It will prompt:
- **Phone number:** `08012345678` (any valid Nigerian number)
- **Password:** (min 8 chars)

Note: no email prompt because we made it optional. The signal auto-creates
your wallet.

### 8. Start everything

```bash
docker compose up
```

### 9. Verify in browser

Open http://localhost:8000/admin/ → log in with your new phone + password.

You should now see three new admin sections:
- **Accounts** — Users
- **Ledger** — Accounts, Journals, Ledger entries
- **Wallets** — Wallets

Click on your user — you should see all the new fields (tier, kyc_tier, referral_code, etc.).
Click on Wallets — you should see one wallet auto-created for your user with balance ₦0.00.

## Run the tests

Tests are the safety net. If any fail, don't proceed.

```bash
docker compose run --rm django pytest
```

You should see all tests pass. The critical ones to look for:

- `test_concurrent_debits_do_not_double_spend` — proves the SELECT FOR UPDATE
  lock actually prevents race conditions
- `test_same_reference_replay_does_not_double_charge` — proves idempotency works
- `test_cannot_update_entry` / `test_cannot_delete_entry` — proves ledger entries
  are truly immutable
- `test_unbalanced_journal_rejected` — proves the double-entry rule is enforced

If all tests pass, the foundation is solid. Ship it.

## What each piece does

### Accounts app
- Users register with a Nigerian phone number (auto-normalized to `+234...`)
- Email is optional but strongly recommended (unlocks free OTP channel)
- Every user gets: `kyc_tier` (0-3 for transaction limits), `tier` (regular/bronze/silver/gold/platinum for pricing), `referral_code` (auto-generated), and a `transaction_pin_hash` (separate from login password, lockable after 5 failures)

### Ledger app
- Double-entry accounting. Every journal has entries summing to zero.
- `LedgerEntry` records are IMMUTABLE. No updates. No deletes. Corrections happen through reversing journals.
- Balances are ALWAYS computed from entries — never stored.
- Idempotency via `unique_together = (journal_type, reference)`.

### Wallets app
- One `Wallet` per user, tied to one ledger `Account` of type `USER_WALLET`.
- `WalletService.debit()` and `.credit()` use `SELECT FOR UPDATE` — no double-spend possible.
- `WalletService.debit_with_split()` supports "buy X, some goes to aggregator cost, some to platform revenue."
- Auto-created via signal when a User is saved.

## What's next (Phase 2)

Once tests are green, we move to:
- **`apps.services`** — Service catalog (airtime, data, cable TV, etc.) with tiered pricing
- **`apps.transactions`** — User-facing transaction model + state machine
- **`apps.aggregators`** — Abstract aggregator interface + Pairgate implementation
- **`apps.payments`** — Monnify integration for wallet funding

## Troubleshooting

**Migrations fail with "relation auth_user already exists":**
You didn't wipe the DB. Run `docker compose down -v` and start over from step 4.

**Concurrent debit test fails:**
Postgres isn't at isolation level READ COMMITTED (default) or higher.
Should never happen with default Postgres config.

**"AUTH_USER_MODEL refers to model 'accounts.User' that has not been installed":**
The `apps.accounts` app wasn't added to `INSTALLED_APPS`. Check that the new
`base.py` was correctly copied over.
