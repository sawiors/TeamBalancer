# Third-Party License Summary

Last reviewed: 2026-05-15

This document summarizes license signals from package metadata in the current virtual environment.

## Runtime dependency set (required to run app)

1. customtkinter 5.2.2
- Metadata license field: Creative Commons Zero v1.0 Universal (CC0-1.0)
- Metadata classifier: MIT License
- Practical impact: permissive

2. darkdetect 0.8.0 (transitive)
- License: BSD-3-Clause
- Practical impact: permissive

3. packaging 26.2 (transitive)
- License expression: Apache-2.0 OR BSD-2-Clause
- Practical impact: permissive

## Build-time dependency set (optional, EXE packaging)

1. pyinstaller 6.20.0
- License field: GPLv2-or-later with special exception
- Practical impact: exception allows building and distributing proprietary/commercial programs

2. pyinstaller-hooks-contrib 2026.5
- Metadata classifiers: Apache Software License, GNU GPLv2
- Practical impact: mixed signals; review exact bundled hooks/files on release

3. altgraph 0.17.5
- License: MIT

4. pefile 2024.8.26
- License: MIT

5. pywin32-ctypes 0.2.3
- License: BSD-3-Clause

## Commercial use and distribution

- Runtime stack is permissive and does not impose strong copyleft obligations.
- EXE build stack includes GPLv2 signals via PyInstaller ecosystem, but PyInstaller itself provides an explicit commercial-distribution exception.
- Keep project LICENSE and applicable third-party notices in distributed artifacts.

## Important note

License metadata can change by version. Re-check before every release when dependencies are updated.
