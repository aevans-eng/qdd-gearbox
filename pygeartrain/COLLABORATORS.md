# Collaboration Guide

## Team
- **Russell (russlib)** — Repo owner, approves all merges to main
- **Aaron (aevans-eng)** — Collaborator with write access

## Git Workflow

**⚠️ IMPORTANT: Do NOT push directly to `main`**

### For Aaron:
1. Create a feature branch: `git checkout -b aaron/feature-name`
2. Make your changes and commit
3. Push to your branch: `git push origin aaron/feature-name`
4. Open a Pull Request to `main`
5. Wait for Russell to review and merge

### Branch naming:
- `aaron/` prefix for Aaron's branches
- `russell/` prefix for Russell's branches
- Descriptive names: `aaron/gear-visualization`, `aaron/fix-tolerance-calc`

### Before pushing:
- Test your code runs without errors
- Commit with clear messages describing what changed

## Permissions
- Aaron has **write** access (can push branches, open PRs)
- Only Russell merges to `main`
- This is a trust-based workflow — no automated branch protection

## Questions?
Ask in the #friend-sandbox Discord channel.
