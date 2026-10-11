#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  printf 'Использование: bash scripts/github_publish.sh ИМЯ_РЕПОЗИТОРИЯ\n' >&2
  exit 1
fi
gh auth status >/dev/null
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  printf 'Не найден Git-репозиторий\n' >&2
  exit 1
fi
if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$1" --public --source=. --remote=origin --push
fi
git push -u origin main
git push -u origin feature/task-assignment-tests
bash scripts/github_setup.sh
gh pr create --base main --head feature/task-assignment-tests --title 'test: проверка переназначения задач' --body-file docs/PR_EXAMPLE.md
