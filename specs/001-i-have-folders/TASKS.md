# Tasks: Media File Organization by Creation Date

**Input**: Design documents from `/specs/001-i-have-folders/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, Click, Pillow, pytest
   → Libraries: file_scanner, date_organizer, file_mover, config_manager
   → Structure: Single project (src/, tests/)
2. Load optional design documents:
   → data-model.md: MediaFile, FolderOperation, FileOperation, Configuration
   → contracts/cli-interface.yaml: organize, scan, config, undo commands
   → research.md: Technical decisions for clarifications
3. Generate tasks by category:
   → Setup: Python project, dependencies, project structure
   → Tests: CLI contract tests, integration scenarios
   → Core: Models, libraries, CLI commands
   → Integration: File operations, config management
   → Polish: Performance, docs, packaging
4. Apply TDD rules:
   → Tests MUST be written first and MUST fail
   → No implementation before tests are red
5. Number tasks T001-T040
6. Mark parallel tasks [P] for different files
7. Validate completeness
8. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Source code**: `src/` at repository root
- **Tests**: `tests/` at repository root
- **Libraries**: `src/lib/` for core libraries
- **CLI**: `src/cli/` for Click commands
- **Models**: `src/models/` for data models

## Phase 3.1: Setup
- [x] T001 Create project structure: src/, tests/, src/lib/, src/cli/, src/models/
- [x] T002 Initialize Python project with requirements.txt (Click, Pillow, python-dateutil, tqdm, pytest, PyYAML)
- [x] T003 [P] Configure pytest.ini and .gitignore for Python project
- [x] T004 [P] Create setup.py for installable package

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests for CLI Commands
- [x] T005 [P] Contract test for 'organize' command in tests/contract/test_organize_command.py
- [x] T006 [P] Contract test for 'scan' command in tests/contract/test_scan_command.py
- [x] T007 [P] Contract test for 'config init' command in tests/contract/test_config_command.py
- [x] T008 [P] Contract test for 'undo' command in tests/contract/test_undo_command.py

### Integration Tests for User Stories
- [x] T009 [P] Integration test: organize folder with mixed media in tests/integration/test_organize_media.py
- [x] T010 [P] Integration test: handle duplicate filenames in tests/integration/test_duplicates.py
- [x] T011 [P] Integration test: verify file before delete in tests/integration/test_safe_move.py
- [x] T012 [P] Integration test: create date folders automatically in tests/integration/test_folder_creation.py
- [x] T013 [P] Integration test: dry-run preview in tests/integration/test_dry_run.py
- [x] T014 [P] Integration test: config file loading in tests/integration/test_config_loading.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [x] T015 [P] MediaFile model in src/models/media_file.py
- [x] T016 [P] FolderOperation model in src/models/folder_operation.py
- [x] T017 [P] FileOperation model in src/models/file_operation.py
- [x] T018 [P] Configuration model in src/models/configuration.py
- [x] T019 [P] OperationLog model in src/models/operation_log.py

### Core Libraries
- [x] T020 File scanner library in src/lib/file_scanner.py (scan folders, extract metadata)
- [x] T021 Date organizer library in src/lib/date_organizer.py (determine target folders)
- [x] T022 File mover library in src/lib/file_mover.py (safe move with verification)
- [x] T023 Config manager library in src/lib/config_manager.py (load/save configuration)
- [x] T024 [P] EXIF reader helper in src/lib/exif_reader.py (extract image metadata)
- [x] T025 [P] Progress reporter in src/lib/progress_reporter.py (progress bars, status updates)

### CLI Commands
- [x] T026 Main CLI entry point in src/cli/main.py (Click app initialization)
- [x] T027 Organize command in src/cli/commands/organize.py
- [x] T028 Scan command in src/cli/commands/scan.py
- [x] T029 Config command group in src/cli/commands/config.py
- [x] T030 Undo command in src/cli/commands/undo.py
- [x] T031 [P] CLI helpers in src/cli/helpers.py (confirmation prompts, output formatting)

## Phase 3.4: Integration
- [x] T032 Wire up file_scanner with EXIF reader for date extraction
- [x] T033 Connect organize command with all libraries (scanner, organizer, mover)
- [x] T034 Implement operation logging throughout the system
- [x] T035 Add resume capability for interrupted operations
- [x] T036 Implement config file validation and migration

## Phase 3.5: Polish
- [ ] T037 [P] Unit tests for date extraction logic in tests/unit/test_date_extraction.py
- [ ] T038 [P] Unit tests for duplicate handling in tests/unit/test_duplicate_names.py
- [ ] T039 Performance test: 1000 files/minute in tests/performance/test_throughput.py
- [ ] T040 [P] Create llms.txt documentation for each library
- [ ] T041 [P] Add comprehensive error messages with recovery suggestions
- [ ] T042 PyInstaller configuration for standalone executable
- [ ] T043 Run quickstart.md scenarios for validation

## Dependencies
- Setup (T001-T004) must complete first
- All tests (T005-T014) MUST complete and fail before any implementation
- Models (T015-T019) can be parallel, no dependencies
- Libraries (T020-T023) depend on models being complete
- CLI commands (T026-T031) depend on libraries
- T026 (main.py) blocks T027-T030
- Integration tasks (T032-T036) require core implementation
- Polish tasks can run after implementation complete

## Parallel Execution Examples

### Launch all contract tests together (T005-T008):
```
Task: "Contract test for 'organize' command in tests/contract/test_organize_command.py"
Task: "Contract test for 'scan' command in tests/contract/test_scan_command.py"
Task: "Contract test for 'config init' command in tests/contract/test_config_command.py"
Task: "Contract test for 'undo' command in tests/contract/test_undo_command.py"
```

### Launch all integration tests together (T009-T014):
```
Task: "Integration test: organize folder with mixed media in tests/integration/test_organize_media.py"
Task: "Integration test: handle duplicate filenames in tests/integration/test_duplicates.py"
Task: "Integration test: verify file before delete in tests/integration/test_safe_move.py"
Task: "Integration test: create date folders automatically in tests/integration/test_folder_creation.py"
Task: "Integration test: dry-run preview in tests/integration/test_dry_run.py"
Task: "Integration test: config file loading in tests/integration/test_config_loading.py"
```

### Launch all models together (T015-T019):
```
Task: "MediaFile model in src/models/media_file.py"
Task: "FolderOperation model in src/models/folder_operation.py"
Task: "FileOperation model in src/models/file_operation.py"
Task: "Configuration model in src/models/configuration.py"
Task: "OperationLog model in src/models/operation_log.py"
```

## Notes
- [P] tasks = different files, no shared dependencies
- Tests MUST fail before implementation (RED phase of TDD)
- Commit after each task with clear message
- Use pytest fixtures for test file creation
- Real file operations, no mocks
- Each library must have CLI interface

## Task Generation Rules Applied
1. **From Contracts**:
   - cli-interface.yaml → T005-T008 (contract tests)
   - Each command → T027-T030 (implementation)
   
2. **From Data Model**:
   - MediaFile → T015
   - FolderOperation → T016
   - FileOperation → T017
   - Configuration → T018
   - OperationLog → T019
   
3. **From User Stories**:
   - Organize by date → T009
   - Handle duplicates → T010
   - Safe file move → T011
   - Auto folder creation → T012
   - Dry run → T013

4. **From Libraries (plan.md)**:
   - file_scanner → T020
   - date_organizer → T021
   - file_mover → T022
   - config_manager → T023

## Validation Checklist
- [x] All CLI commands have contract tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks are truly independent
- [x] Each task specifies exact file path
- [x] No parallel task modifies same file

## Task Count Summary
- Setup: 4 tasks
- Tests (TDD): 10 tasks
- Models: 5 tasks
- Libraries: 6 tasks
- CLI: 6 tasks
- Integration: 5 tasks
- Polish: 7 tasks
- **Total: 43 tasks**

Ready for execution following strict TDD approach.