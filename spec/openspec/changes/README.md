# OpenSpec Changes Directory

This directory contains **in-flight changes** — proposed modifications to the Software Fabric.

Each change gets its own folder containing OpenSPEC artifacts:

```
changes/
├── <change-slug>/          ← One folder per in-flight change
│   ├── proposal.md         ← Intent, scope, acceptance criteria (Product Owner)
│   ├── design.md           ← Technical approach, ADRs, diagrams (Architect)
│   ├── tasks.md            ← Numbered implementation checklist (Architect)
│   └── specs/              ← Delta specs (ADDED / MODIFIED / REMOVED)
│       └── <domain>/
│           └── spec.md
└── archive/                ← Completed changes (merged into specs/)
    └── YYYY-MM-DD-<slug>/
```

## Lifecycle

```
/opsx:propose <slug>  →  changes/<slug>/ created
/opsx:apply           →  tasks implemented, PR opened
/opsx:sync            →  delta specs merged into specs/ (preview)
/opsx:archive         →  changes/<slug>/ moved to changes/archive/
```

## Creating a New Change

Using VS Code Copilot:
```
/opsx:propose <your-idea-slug>
```

Or copy the idea template:
```
cp spec/openspec/templates/idea-to-spec.md spec/openspec/changes/<slug>/proposal.md
```

See `spec/openspec/config.yaml` for project-level settings.
See `spec/openspec/specs/` for the current source-of-truth specs.
