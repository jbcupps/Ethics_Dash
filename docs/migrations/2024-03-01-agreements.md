# Migration: Agreements & Agreement Actions

## Purpose
Adds the collections and indexes needed for the agreement lifecycle:
- `agreements` collection (status, parties, terms, model snapshots)
- `agreement_actions` collection (accept/decline/counter/comment history)

## Apply
1. Deploy the backend code that creates the indexes in `backend/app/__init__.py`.
2. Start the API so the MongoDB indexes are created on boot.

## Rollback
1. Drop indexes if needed:
   - `agreements_status_idx`
   - `agreements_created_at_idx`
   - `agreement_actions_agreement_id_timestamp_idx`
2. Optionally drop collections if you need to fully remove the feature:
   - `agreements`
   - `agreement_actions`

> Note: Dropping collections will permanently delete agreement history.
