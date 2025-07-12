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
   # Update version in pyproject.toml
   poetry version [patch|minor|major]
   # or manually edit pyproject.toml line 3: version = "X.Y.Z"
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
   git add pyproject.toml CHANGELOG.rst
   git commit -m "Bump version to X.Y.Z"
   git push origin release/X.Y.Z
   git push origin X.Y.Z
   ```

### 3. Wait for CI and Merge

1. **Wait for CI to Pass**
   - Monitor GitHub Actions to ensure all tests pass

2. **Merge Release Branch**
   Merge PR using GH button.

### 4. Create GitHub Release

1. **Create GitHub Release**
   - Go to [GitHub Releases](https://github.com/sunscrapers/djoser/releases)
   - Click "Create a new release"
   - Select the tag you just created (X.Y.Z)
   - Title: `X.Y.Z`
   - Description: Copy relevant section from CHANGELOG.rst
   - Set git tag
   - Mark as pre-release if it's a pre-release (e.g., `2.4.0a1`)
   - Publish release

### 5. Automated Publishing

Once a GitHub release is created, the CI/CD pipeline automatically:

1. **Validates** package version matches the git tag
2. **Compiles** translations (`pybabel compile`)
3. **Builds** the package (`poetry build`)
4. **Publishes** to PyPI:
   - Pre-releases → Test PyPI
   - Stable releases → Production PyPI

The publish workflow is triggered by the `on.release.types.released` event.

## Version Numbering

- **Patch** (X.Y.**Z**): Bug fixes, minor improvements
- **Minor** (X.**Y**.0): New features, backwards compatible
- **Major** (**X**.0.0): Breaking changes

## Notes

- The `publish_pypi.yml` workflow handles all PyPI publishing
- Translations are automatically compiled during the release process
- Version verification ensures pyproject.toml matches the git tag
- Test PyPI is used for pre-releases to validate the packaging

## Troubleshooting

- If publishing fails, check the GitHub Actions logs
- Ensure all translations compile without errors
- Verify the version in pyproject.toml matches your git tag exactly
- Make sure the CHANGELOG.rst is properly formatted
