---
name: release
description: Release a new djoser version - review the diff since the last release, write the changelog entry, bump the version, verify everything locally, and prepare the tag for the user to push
---

# Release a new djoser version

Prepare and verify a release end-to-end. The user's `git push origin X.Y.Z`
is the only action that triggers anything external: the tag push starts the
`Release` workflow (validate → test matrix → build → PyPI → GitHub release).
Never push the tag yourself. Never run `uv publish` or `gh release create`
manually — CI does that.

Work through the stages in order. Do not skip a verification because it
"probably passes"; the whole point of this skill is that the release is
checked before the tag exists.

## 1. Establish scope

1. `git fetch origin` and make sure the local `master` matches
   `origin/master` with a clean working tree.
2. Find the last release: `LAST_TAG=$(git describe --tags --abbrev=0 origin/master)`.
3. Review everything since then: `git log --oneline $LAST_TAG..origin/master`
   and the full `git diff $LAST_TAG..origin/master`. Read the diff, not just
   the commit subjects — changelog entries must describe user-facing behavior,
   and commit messages sometimes undersell or oversell what changed.
4. Summarize the user-facing changes for the user and agree on the new
   version number:
   - patch = bug fixes, minor = backwards-compatible features,
     major = breaking changes
   - a PEP 440 pre-release suffix (`a1`, `b1`, `rc1`) publishes to PyPI like
     any other version, but pip/uv never resolve to it without `--pre` or an
     exact pin; suggest one first when the diff is large or risky
5. If there is nothing user-facing to release, say so and stop.

## 2. Prepare the release branch

1. `git checkout -b release/X.Y.Z origin/master`
2. Set the version in `pyproject.toml` (`[project] version`), then run
   `uv lock` — the lockfile records the project's own version and the CI
   lock-file check fails if it is stale.
3. Update `CHANGELOG.rst`:
   - new section at the top, matching the existing format exactly:
     overline/underline dashes, `` `X.Y.Z`_ (YYYY-MM-DD) `` heading, `*`
     bullets with issue/PR links
   - a `.. _X.Y.Z: https://github.com/sunscrapers/djoser/compare/PREV...X.Y.Z`
     link definition at the bottom
   - every notable change found in stage 1 must be reflected; nothing in the
     entry may be missing from the diff
   - the CI extracts this section verbatim as the GitHub release notes, and
     fails a stable release if the section is missing
4. Show the changelog entry to the user and get approval before continuing.

## 3. Verify locally

Run all of these; all must pass:

1. `make test` — full suite
2. `make run-hooks` — pre-commit checks (needs `.venv/bin` on `PATH`)
3. `make build` — translations compile and the package builds
4. `uv lock --check` — lockfile consistent with `pyproject.toml`

Report the results honestly; a failure here aborts the release until fixed.

## 4. Land the bump on master

1. Commit `pyproject.toml`, `uv.lock` and `CHANGELOG.rst` as
   `Bump version to X.Y.Z`.
2. Push the branch and open a PR against `master`; wait for the user to
   merge it (the repo squash-merges).
3. After the merge: `git fetch origin` and confirm `origin/master` now
   carries the bump (`uv version --short` on that commit equals `X.Y.Z`).

## 5. Tag and hand over

1. Tag the merged commit: `git tag X.Y.Z origin/master` — tags are bare
   `X.Y.Z`, no `v` prefix, matching every historical djoser tag (stable tags
   must point at a commit on `master` — CI enforces this).
2. Do NOT push the tag. Tell the user to run:
   ```bash
   git push origin X.Y.Z
   ```
3. Point them at the Actions tab to watch the `Release` workflow. If it
   fails, the fix path is: correct the problem, `git push --delete origin
   X.Y.Z`, delete the local tag, and re-run this skill's relevant stages.
