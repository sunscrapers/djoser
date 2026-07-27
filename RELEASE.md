# Djoser Release Process

This document outlines the process for creating a new release of Djoser.

## Release Workflow

Djoser uses [Semantic Versioning](http://semver.org/) and follows this release process:

### 1. Create Release Branch

1. **Checkout and Create Release Branch**
   ```bash
   git checkout master
   git pull origin master
   git checkout -b release/X.Y.Z
   ```

### 2. Prepare Release

1. **Update Version Number**
   ```bash
   # Manually edit pyproject.toml line 3: version = "X.Y.Z"
   # Then update the lockfile — it records djoser's own version,
   # and CI's `uv lock --check` fails if it is stale:
   uv lock
   ```

2. **Update CHANGELOG.rst**
   - Add new version section at the top following existing format:
   ```rst
   ---------------------
   `X.Y.Z`_ (YYYY-MM-DD)
   ---------------------

   * List of changes
   * Bug fixes
   * New features
   ```

   Don't forget to add a diff link at the bottom of CHANGELOG.rst

3. **Build locally**
   ```bash
   make build
   ```
   Just to check if everything works.

4. **Run Tests & Quality Checks**
   ```bash
   make test
   make run-hooks  # pre-commit checks
   ```

5. **Commit and Push Release Branch**
   ```bash
   git add pyproject.toml uv.lock CHANGELOG.rst
   git commit -m "Bump version to X.Y.Z"
   git push origin release/X.Y.Z
   ```

### 3. Wait for CI and Merge

1. **Wait for CI to Pass**
   - Monitor GitHub Actions to ensure all tests pass

2. **Merge Release Branch**
   Merge PR using GH button.

### 4. Tag the Release

Tag the merged commit and push the tag. Pushing the tag is the only action
that triggers publishing — everything after it happens in CI.

```bash
git checkout master
git pull origin master
git tag X.Y.Z
git push origin X.Y.Z
```

For pre-releases use a PEP 440 suffix, e.g. `2.4.0rc1` (`aN`, `bN` and `rcN`
are recognized).

### 5. Automated Release Pipeline

Pushing a tag triggers the `Release` workflow, which:

1. **Validates** the release before building anything:
   - the tag looks like `X.Y.Z` (optionally with an `aN`/`bN`/`rcN` suffix);
     anything else fails validation and nothing is built
   - `pyproject.toml` version matches the tag
   - stable tags point at a commit that is on `master`
   - `CHANGELOG.rst` contains a section for the version (required for stable
     releases; optional for pre-releases) — it becomes the release notes
2. **Runs the full test suite** (the same matrix as `test-suite.yml`)
3. **Compiles** translations (`pybabel compile`) and **builds** the package
   (`uv build`)
4. **Publishes** the built distribution:
   - Pre-releases → Test PyPI (`testpypi` environment)
   - Stable releases → PyPI (`pypi` environment)
5. **Creates the GitHub release** with the changelog section as its notes and
   the built distribution attached (only after publishing succeeded)

If any validation or test fails, nothing is built or published — fix the
problem, delete the tag (`git push --delete origin X.Y.Z`), and tag again.

## Claude Code Skill

Steps 1–4 are automated as a Claude Code skill: run `/release` in this
repository and Claude reviews the diff since the last release, drafts the
CHANGELOG.rst entry, bumps the version, runs the local checks, prepares the
release PR and creates the tag — leaving the final `git push origin X.Y.Z`
to you.

## Version Numbering

- **Patch** (X.Y.**Z**): Bug fixes, minor improvements
- **Minor** (X.**Y**.0): New features, backwards compatible
- **Major** (**X**.0.0): Breaking changes

## One-Time Setup

The pipeline authenticates to PyPI with [trusted publishing](https://docs.pypi.org/trusted-publishers/)
(OIDC) — no API tokens are stored in GitHub secrets. It has to be configured
once per index:

- On [PyPI](https://pypi.org/manage/project/djoser/settings/publishing/) add a
  trusted publisher: owner `sunscrapers`, repository `djoser`, workflow
  `release.yml`, environment `pypi`
- On [Test PyPI](https://test.pypi.org/manage/project/djoser/settings/publishing/)
  add the same with environment `testpypi`
- In the GitHub repository settings, create the `pypi` and `testpypi`
  environments; optionally add required reviewers to `pypi` to get a manual
  approval gate before publishing

## Notes

- The `release.yml` workflow handles the entire release: validation, tests,
  build, PyPI upload and the GitHub release
- Translations are automatically compiled during the release process
- Test PyPI is used for pre-releases to validate the packaging

## Troubleshooting

- If the pipeline fails, check the GitHub Actions logs — validation failures
  (version mismatch, missing changelog entry, tag not on master) are reported
  before anything is built or published
- Ensure all translations compile without errors
- Make sure the CHANGELOG.rst is properly formatted
- To retry a failed release: fix the problem, delete the tag locally and
  remotely, then tag and push again
