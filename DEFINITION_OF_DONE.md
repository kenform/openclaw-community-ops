# Definition of Done (DoD)

A task is "Done" only if all criteria below are met:

1. Functional result
- Required action completed in target system/channel.
- No blocking errors remain.

2. Verification
- Checked via logs/report/output (not assumption).
- If applicable, before/after state captured.

3. Safety
- No secrets/tokens/sessions exposed.
- No destructive side effects outside approved scope.

4. Documentation
- Task status updated in `memory/tasks.md`.
- Relevant note/report stored in workspace.

5. Reproducibility
- If automation-related: script/config committed.
- If recurring: timer/schedule documented or enabled.

6. Handoff clarity
- User receives concise status: done / pending / next step.
