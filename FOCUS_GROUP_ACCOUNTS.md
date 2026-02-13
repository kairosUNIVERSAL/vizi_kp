# Focus Group Accounts

These accounts are auto-created on backend startup by `backend/app/initial_data.py`.

| Email | Password | Role | Company profile |
|---|---|---|---|
| `focus.admin@kp.local` | `FocusAdmin2026!` | Admin | Focus Admin Ceiling (Moscow) |
| `focus.sales@kp.local` | `FocusUser2026!` | User | Focus Sales Studio (Saint Petersburg) |
| `focus.ops@kp.local` | `FocusUser2026!` | User | Focus Operations Team (Kazan) |
| `focus.newcomer@kp.local` | `FocusUser2026!` | User | Focus Newcomer Branch (Novosibirsk) |

## What differs between these accounts

1. Access level:
   - `focus.admin@kp.local` has admin access (`/api/admin/*`, admin page in UI).
   - Other accounts are regular users.
2. Data isolation:
   - Each account has its own company and own estimates/price items (`company_id` isolation).
   - Users do not see or modify each other's data.
3. Preset company defaults:
   - Warranty, discount, validity period, messenger and city differ across accounts.
   - This gives focus-group participants different starting scenarios.
4. Price list structure:
   - Focus accounts reuse the source admin company's real price list structure.
   - No mock categories or mock positions are added.

## Logs for focus-group analysis

The app writes:
1. Request-level logs for all `/api/*` calls into `activity_logs` table.
2. Auth events (`login_success`, `login_failed`, `register_success`) into `activity_logs`.

Admin can read recent logs from:

`GET /api/admin/activity-logs?limit=100`

Optional filters:
- `user_id`
- `action`

## Security note

Rotate these passwords before any production/public deployment.
