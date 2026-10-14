# Translator extension list

[中文](README.md)

This repository lists the extensions that [Translator](https://github.com/KlaraGraff/XL_Translator) users can find and install directly under "Browse extensions" on the Extensions page. Each extension has one entry, `extensions/<id>.json`; its code and package live in the author's own repository. Translator reads `index.json`, which a workflow builds from these entries.

To make an extension of your own, start from the [extension template](https://github.com/KlaraGraff/XL_Translator-extension-template).

## How to submit

1. Test and publish the extension in your own repository as the template's README describes. Pushing a `v<version>` tag makes the Release workflow build the zip and print the entry in its log.
2. Fork this repository and add `extensions/<id>.json` with that entry; the file name must match `id`. Write `summary` in Chinese, English and French, a sentence or two each: which files it translates and what it leaves alone.
3. Open a pull request and fill in the template. The checks then:
   - validate the entry against `schema/entry.schema.json` and Translator's own rules;
   - download the zip from every address in `download` and compare its size and SHA-256;
   - run Translator's `adapter test` on the package (the same checks as an install) and try the extension on its `samples/`.
4. For a new version, change `version`, `download`, `sha256` and `size` in the same entry file and open another pull request.

## Review

- An entry is merged once every check passes and a maintainer has read the code and found nothing suspicious (going online, reading files unrelated to the translation, obfuscated code, behaviour that does not match the summary). Claude currently reads the code and merges on the maintainer's behalf, then reports in the Translator project.
- On merge, `reviewed_at` and `reviewed_by` are filled in and `status` is `reviewed`. `official` is only for extensions maintained by the Translator project.
- A review covers the version submitted. Extensions run with the user's permissions, so "reviewed" is not a guarantee; users are told before installing to install only from sources they trust.

## Removal

When an extension has a problem (malicious behaviour, a serious defect, a license issue, or the author asks), deleting its entry removes it: `index.json` is rebuilt and it no longer appears under "Browse extensions". Users who already installed it are not affected and can uninstall it on the Extensions page. Authors can also open a pull request removing their own entry.

## Entry fields

| Field | Meaning |
| --- | --- |
| `id` | Same as `id` in the extension's `adapter.json`; the file is `<id>.json` |
| `name`, `summary` | Name and summary in Chinese, English and French |
| `extensions` | File extensions it handles, as in `adapter.json` |
| `author`, `repo`, `license` | Author, home page, license |
| `version`, `adapter_api_version`, `min_app_version` | Version, protocol version, lowest Translator version it needs (may be empty) |
| `download` | Where the zip can be downloaded, tried in order; every address must serve the same file |
| `sha256`, `size` | The zip's SHA-256 and size in bytes, at most 2 MB |
| `tags` | Search tags, may be empty |
| `status`, `reviewed_at`, `reviewed_by` | Filled in by the maintainer on merge |

## Files

- `extensions/`: the entries.
- `index.json`: built by `.github/workflows/index.yml` whenever main changes; do not edit it by hand.
- `packages/`: packages of the extensions maintained by the Translator project.
- `schema/entry.schema.json`: the entry format.
- `scripts/`: building the index (`build_index.py`, standard library only) and checking entries (`check_entries.py`, needs Translator's source).
