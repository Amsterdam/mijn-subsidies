# Mijn subsidies
API voor leveren van Subsidie informatie aan Mijn Amsterdam Front-end


## Build & deploy
The project is built automatically by a Jenkins server. If the build and tests succeed, the main branch automatically deploys to the acceptance server.

### Releasing
If new code can be released to production, the `release.sh` script can be used. The script automatically increments the version and assigns a git tag to the new release commit.
The `release.sh` script can be used with regular semver parameters: `release.sh [--major|--minor|--patch]`.