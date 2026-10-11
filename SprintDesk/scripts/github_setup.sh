#!/usr/bin/env bash
set -euo pipefail
if ! command -v gh >/dev/null 2>&1; then
  printf 'Требуется GitHub CLI (gh)\n' >&2
  exit 1
fi
gh auth status >/dev/null
repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
if [ -z "$repo" ]; then
  printf 'Откройте каталог репозитория GitHub с настроенным origin\n' >&2
  exit 1
fi
gh api --method PUT "repos/$repo/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["tests"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"dismiss_stale_reviews": true, "required_approving_review_count": 1},
  "restrictions": null,
  "required_conversation_resolution": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
printf 'Правила защиты main настроены для %s\n' "$repo"
