---
name: github-workflow
description: Safely manage GitHub research branches, small commits, PRs, CI runs, logs, artifacts and traceable changes.
---
# GitHub Workflow

## When to use
Before editing repository files, running GitHub Actions, reviewing commits, publishing artifacts or merging branches.

## Procedure
1. Confirm repository, active branch, latest commit, file existence and target paths. Do not assume default branch or access rights.
2. Inspect AGENTS.md and applicable skills; define edit scope and whether researcher approval is required.
3. Make minimal coherent commits; avoid overwriting unrelated changes. For sequential changes to a path, fetch the latest blob SHA.
4. Keep research code, documentation and deployment changes separately reviewable. Never merge into main or publish private content without approval.
5. Validate YAML syntax, paths, trigger conditions and matrix parameters. `workflow_dispatch` availability may depend on default-branch workflow registration; use tested triggers when appropriate.
6. After execution, inspect **each matrix job** and failed step logs, not merely top-level status. Record run ID, commit, branch, artifact IDs and retention.
7. For failed runs, identify precise failing assertion, propose minimal fix, assess impact and rerun affected checks. Do not describe queued/in-progress as successful.
8. Archive large data outside Git when appropriate; do not commit generated multi-million-row CSVs or credentials. Preserve reproducibility metadata.
9. Verify changed files on GitHub after writes; summarize what was and was not tested.

## Output
Change summary, commit links, test/run status, artifact provenance and outstanding risks.

## Acceptance
Changes are auditable, on the intended branch, with no unapproved mechanism changes or unverified claims.
