# What a Claude Code session cannot do on GitHub

Seen from cloud sessions working on these repositories (2026-11). GitHub traffic goes through a proxy that allows the REST API and a limited set of git operations. When something is refused, do not look for a way around it: say what was refused, do the rest, and leave that step to the owner.

| Refused | What it means here | Do instead |
|---|---|---|
| Pushing a tag | `git push origin v1.2.3` is rejected | Let the repository's release workflow make the tag (releases.md). For a hand-bump repository, bump the version in a pull request; oncemore's tag is pushed by the owner |
| Deleting a branch | neither `git push --delete` nor `DELETE /git/refs/heads/...` works | Leave merged branches; list them in the report if they matter. `bot/repin` is rebuilt by its workflow, never deleted |
| GraphQL | `https://api.github.com/graphql` returns 403, so `gh pr list`, `gh pr view`, `gh pr ready`, `gh issue view`, `gh pr merge` and others fail | Use REST: `gh api repos/<o>/<r>/pulls?state=open`, `gh api repos/<o>/<r>/issues/N`, `gh api -X PUT repos/<o>/<r>/pulls/N/merge -f merge_method=squash -f sha=<head>` |
| Draft → ready for review | `gh pr ready` is GraphQL; there is no REST field for it | Open pull requests as ready (not draft) in the first place. A draft opened by a workflow (a `review` re-pin) waits for the owner to mark it ready |
| Repository settings (`PATCH /repos/<o>/<r>`) | default branch, merge options, auto-delete of head branches and the like cannot be changed | Name the setting and give the owner its settings page link |
| A comment that mentions `@coderabbitai` | the comment is refused | Do not ask for a CodeRabbit review from the session; read the reviews it posts on its own, and merge without one if it does not review |

Also:

- Open a pull request with `gh api repos/<o>/<r>/pulls -f title=... -f head=<branch> -f base=main -f body=...` (not `gh pr create`).
- Labels: `gh api -X POST repos/<o>/<r>/issues/N/labels -f 'labels[]=feature'`.
- Workflow runs: `gh api -X POST repos/<o>/<r>/actions/workflows/<file>/dispatches -f ref=main`, then read `.../actions/workflows/<file>/runs`.
- A workflow started by a push or pull request made with a workflow's `GITHUB_TOKEN` does not run; that is GitHub's rule, not the proxy's (see repin.md for how the re-pin works around it).
