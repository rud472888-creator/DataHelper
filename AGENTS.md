# DataHelper project guidance

For an explicit Hermes staged delivery, Hermes coordinates Plan → Implement → QA → Fix → Re-QA and advances only after a recorded QA pass. Use `docs/stage.md` and the stage reports under `docs/reports/` as the durable state. Keep development and QA roles separate, and use a fresh session for each stage run.

For ordinary edits, reviews, and questions, follow the user's task directly. Read relevant files and run focused verification without creating stage reports or a new session unless the task calls for the Hermes workflow.
