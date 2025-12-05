# Project: pickup-latest-version-file

## Overview
A script to organize files in a directory by identifying versioned files (e.g., `file_v1.txt`, `file_v2.txt`) and moving older versions to an `old` subdirectory, keeping only the latest version.

## Requirements
-   **Language**: Python
-   **Methodology**: TDD (Test-Driven Development)
-   **Versioning**:
    -   Suffixes like `_v{N}` (e.g., `_v1`, `_v2`).
    -   Timestamps (e.g., `_20251114...`).
    -   Files without version suffixes may exist.
-   **Action**: Move non-latest files to `old/`.

## User Preferences
-   Use `uv` for package management.
-   Communication in Japanese.
