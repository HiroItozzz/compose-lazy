## v0.6.2 - 2026-06-03
> Added migration notice to help messages.

## v0.6.1 - 2026-05-31

> Final release under the `fast-dcp` package name. Starting with v0.7.0, the package is published as `compose-lazy`.

### Added
- `dcp ws register(reg)` now allows entering `0` to input a new workspace name when existing workspaces are listed
- `dcp ws up/restart/stop/down` now shows a clear error message when a registered workspace directory no longer exists, instead of silently failing

### Fixed
- Fix partial selections persisting across retries in interactive selection
- Fix misleading "Docker is not found." error when workspace directory is missing or stale
- Fix unexpected errors being silently dropped; now logged at DEBUG level when `FAST_DCP_DEBUG=true`
- Fix debug logging being active unconditionally; `StreamHandler` is now only added when `FAST_DCP_DEBUG=true`

## v0.6.0 - 2026-05-30
 
### Added
 
**`dcp workspace(ws)` command — operate multiple repositories at once**
 
A new `workspace` command lets you register named groups of repositories and run docker compose commands across all of them in one shot.
 
```bash
# Register repositories to a workspace
$ dcp ws register
Please enter a new directory path: /path/to/repo
Please enter a new workspace name: myproject
☑ Registered new path to myproject: /path/to/repo
 
# Launch all repos in a workspace
$ dcp ws up
☑ Found 1 registered workspace.
    1. myproject
Enter your choice: 1
▷ Executing `docker compose up -d` in `/path/to/repo`.
```
 
**Subcommands**
 
| Command | Description |
|---|---|
| `dcp ws register(reg)` | Register a new repository to a workspace interactively |
| `dcp ws delete(del)` | Delete a repository from a workspace interactively |
| `dcp ws list(li)` | List all registered workspaces and their repositories |
| `dcp ws up(u)` | Run `docker compose up -d` for all repos in a workspace |
| `dcp ws restart(re)` | Run `docker compose restart` for all repos in a workspace |
| `dcp ws stop(s)` | Run `docker compose stop` for all repos in a workspace |
| `dcp ws down` | Run `docker compose down` for all repos in a workspace |
 
Workspace configuration is stored in `~/.config/fast-dcp`.

### Fixed
- Fix non-positive integer input (`0`, negative numbers) in interactive selection silently selecting wrong entries

## v0.5.3 - 2026-05-17
- Fixed `exec`/`run` commands appending `bash` after user-specified command (e.g. `dcpe pytest` was executing `docker compose exec <service> pytest bash`)

## v0.5.2 - 2026-05-13 (YANKED)

- Fixed duplicate log output when `setup_logger` is called multiple times
- Fixed `exec`/`run` commands accepting empty service name selection

## v0.5.1 - 2026-05-13

- `dcpe uv run pytest` style commands now auto-detect that the first token is not a service name and fall back to interactive selection
- Improved error message when no compose files are found
- Invalid compose file type now falls back to interactive selection instead of processing as-is
- Internal refactoring

## v0.5.0 - 2026-05-13
- Added `-s` option for interactive service name selection (available for all subcommands)
- Invalid compose file type now falls back to interactive selection instead of warning

## v0.4.0
- Added `-f`, `-pf`, `-p` options to all subcommands (`restart`, `ps`, `logs`, `stop`)

## v0.3.0

**Interactive profile selection for `--profile` option**

Running `dcp up -pf` (or any command with `-pf`) now auto-detects profiles from your docker-compose files and lets you choose interactively.

```bash
$ dcpu -pf
☑ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'Q' to quit:
```

**`--wait` option for `up` command**
`dcpu -w` / `dcp up -w` now supports `docker compose up --wait`, blocking until all services are healthy.
```bash
dcpu -w
dcpu -w -b
```

**`-f`, `-p`, `-pf` options added to `run` command**
**`restart` alias changed from `r` to `re`**

## v0.2.0

**Interactive file selection for `--file` option**

Running `dcpu -f` now auto-detects docker-compose files in your project and lets you choose interactively.

```bash
$ dcpu -f
☑ Found 2 docker-compose files!
    1. docker-compose.yml
    2. docker-compose.experiment.yml
Enter your choices (e.g., 1,3,4) or 'Q' to quit:
```

## Internal
Refactored the return type of the `--project` option from `list` to `str`.


## v0.1.0

### Features
- Add `run` command
- Add `--remove-orphans` option to `dcp down`
- Add `-st` abbreviation to `--status` option

### Improvements
- Improve logging config; make dotenv optional for dev use
- Move `setup_logger` call into each entrypoint function
- Add `NullHandler` in `__init__.py` for library use
- Add `py.typed` marker for PEP 561 compliance

### Fixes
- Fix `__package__` None type issue in `version()`
- Fix pyproject.toml scripts to point directly to `fast_dcp.main`

### Other
- Minor cleanups in `process.py` and `main.py`
- Add tests for `setup_logger`
- Update README

## v0.0.2 

### Bug Fixes
- Fix unhandled KeyboardInterrupt when stopping containers with Ctrl+C (dcp up etc.)

### Improvements
- dcp ps now accepts service names as arguments
- dcp ps now supports --all / -a and --status options

### Internal
- Add test cases for KeyboardInterrupt handling
- Add test cases for dcp ps new options
- Rename ArgDefiner to ArgBuilder
