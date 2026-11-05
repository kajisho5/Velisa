# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities privately using GitHub's built-in reporting
flow, not a public issue:

1. Go to this repository's **Security** tab.
2. Select **Advisories** → **Report a vulnerability**.

This opens a private advisory visible only to the maintainer, so the details aren't
public until a fix is ready.

## Before you run it

`install.sh` is meant to be piped from `curl`, so read what it does before running it:
[README → Quick start → *Before you run it*](README.md#quick-start) shows the `--dry-run`, what is
cloned (the latest default branch, `main`, of each repository in `ecosystem.json`, unpinned) and where it writes.
The installer's own network access is `git clone`/`pull` from `github.com/kajisho5/*`, `pip install`
(pip itself and the cloned checkouts' dependencies, from PyPI) and `npm ci` (the npm registry); it never
uses `sudo` or installs system packages. Its last step runs `video-agent doctor` from the cloned
agent, which is that repository's code.

## Scope

This repository (`Velisa`) is architecture, contracts, and a read-only
ecosystem dashboard (see `dashboard/README.md` for its own security notes on how it
handles GitHub tokens). It has no server, no user data store, and no published package
of its own today. If your report concerns one of the Skill repositories or
`video-production-agent` that this project describes, please report it in that
repository instead, using the same private-advisory flow.
