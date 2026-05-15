# Dependency License Policy

Purpose: keep this project free from strong copyleft obligations and avoid unexpected license constraints.

## Allowed by default

- MIT
- BSD-2-Clause, BSD-3-Clause
- Apache-2.0
- ISC
- CC0-1.0

## Review required before adding

- MPL-2.0, LGPL variants, EPL variants, CDDL

## Not allowed

- GPL-2.0, GPL-3.0, AGPL-3.0 and similar strong copyleft licenses

## Contribution rule

Before adding or updating dependencies:

1. Check license metadata of the package and its transitive dependencies.
2. If a package is missing clear metadata, check official repository/license file.
3. If package falls under Review required or Not allowed, do not merge until decision is documented.
4. Update THIRD_PARTY_LICENSES.md when dependency versions change.

## Packaging/distribution checklist

1. Include this project LICENSE file in distributed artifacts.
2. Include third-party license notices when required.
3. Re-run license review on release branch.
