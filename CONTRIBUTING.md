# Contributing to Workshop

## 1. Project authority

The human project owner has final authority over requirements, architecture, scope, and acceptance of changes.

AI agents and contributors implement only the assigned task. They must not independently expand scope, redesign the architecture, or change established functional decisions.

## 2. Main branch

* `main` is the protected integration branch.
* Work must not be performed directly on `main`.
* Every task must be developed on a dedicated branch.
* Changes enter `main` only after human review and approval through a Pull Request.

## 3. Starting a task

Before making changes, the contributor must:

1. Read `AGENTS.md` and the relevant project documentation.
2. Inspect the current branch and working tree.
3. Synchronize with the latest `origin/main` when appropriate.
4. Create a task-specific branch from the appropriate base.
5. Confirm the task scope and acceptance criteria.

Do not overwrite, discard, or incorporate unrelated changes.

## 4. Branch naming

Use descriptive prefixes:

* `feat/` — new functionality.
* `fix/` — bug fixes.
* `test/` — tests.
* `docs/` — documentation.
* `refactor/` — internal restructuring without intended behavior changes.
* `chore/` — maintenance and tooling.

Examples:

* `feat/procedure-versioning`
* `test/workshop-order-states`
* `docs/contribution-workflow`

## 5. Task scope

Each branch should address one clearly defined task.

* Keep changes small and reviewable.
* Follow the approved architecture and functional specification.
* Avoid unrelated refactoring and unrequested dependencies.
* If a requirement is ambiguous, documents conflict, or an architectural decision is needed, stop and ask the project owner.

## 6. Commits

* Use clear, descriptive commit messages.
* Keep each commit focused on a coherent change.
* Do not commit secrets, credentials, local configuration, database dumps, or unrelated files.
* Do not amend, rewrite, or delete existing commits without authorization.
* Contributors must not push directly to `main`.

## 7. Verification

Before opening a Pull Request:

1. Run the tests relevant to the change.
2. Run additional checks required by the task.
3. Inspect the final diff.
4. Confirm that no unrelated or sensitive files are included.
5. Report exactly which checks passed, failed, or could not be run.

Never claim that a test or check passed unless it was actually executed and its result verified.

## 8. Pull Requests

Every change intended for `main` must be submitted through a Pull Request.

The Pull Request must describe:

* The problem or task addressed.
* The implementation and relevant design decisions.
* Files or components changed.
* Tests and checks performed, including their actual results.
* Known limitations, risks, and pending decisions.

Keep the Pull Request limited to its assigned task.

## 9. Review and integration

The project owner reviews the implementation, tests, scope, security, and compliance with the approved architecture.

The project owner decides whether to approve, request changes, or reject the Pull Request.

No contributor or AI agent may merge a Pull Request into `main` without explicit authorization from the project owner.

## 10. Security and data integrity

* Enforce permissions on the server side, not only in the interface.
* Preserve traceability and the integrity of completed inventory movements and business records.
* Do not introduce unapproved external services, paid dependencies, or Enterprise-only dependencies.
* Verify compatibility with the target Odoo version before relying on APIs.

## 11. Completion report

At the end of each task, report:

1. What was implemented.
2. Which files changed.
3. Which tests and checks were executed and their results.
4. Known limitations or unresolved issues.
5. Any decision required from the project owner.

A task is not considered accepted merely because its code has been written or pushed. Acceptance requires the project's review process.
