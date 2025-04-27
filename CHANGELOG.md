# v1.0.0
**Full Changelog**: https://github.com/kayake/cerberus/compare/v0.0.1-beta...v1.0.0

## New Features

- Saving payloads according to templates and wordlists using the database `Pyvel`.
- Support for multiple wordlists, with wordlist processing parallelized across multiple processes.

> [!CAUTION]
> This feature requires substantial RAM and CPU resources.

- Version verification.

## Changes

- Traditional loop replaced with UvLoop.
- Cerberus architecture significantly streamlined, resulting in a smaller footprint.
- Payloads pre-processed for enhanced attack speed.
- Cache management.
- Attack initiation simplified: Configure the attack via `configs/attack.yaml` (or a custom configuration file).
- Log records enhanced with improved detail and formatting (verbose options).
- Added the directory `wordlists` for custom wordlists without causing issues with GitHub updates.

<sub>
🅘 For more information, refer to the <a href="https://github.com/kayake/cerberus/README.md">documentation</a>.
</sub>

# v0.0.1-beta
- HTTP requests with [`requests`](https://pypi.org/project/requests/).
- Flexible response validation:
    - JSON (keys, values, and both).
    - Status code.
    - Status text.
- Custom shell.
- Proxy and Tor support.
- Pretty logs.