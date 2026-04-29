# Pipeline Stage State

This file is the canonical durable state source for the Frame Proof PDF Generator pipeline.

## Machine-Readable State

STAGE_STATE_START
{
  "pipeline_status": "ready_for_next_prompt",
  "current_stage": 0,
  "current_subphase": "Plan",
  "current_lane": "Dev",
  "gate_status": "PLAN_COMPLETE",
  "source_spec_path": "docs/source/frameproof_tech_spec_ko.md",
  "source_spec_origin": "Docs/frameproof_tech_spec_ko.md",
  "next_prompt": "[Stage 0-Implement]",
  "next_prompt_file": "Docs/frameproof_prompt_pack/prompts/stage0_implement.md",
  "last_terminal_action": "STOP_ESCALATE",
  "last_result": "stage_0_plan_written",
  "blocker": null,
  "human_gate_required": true,
  "human_gate_reason": "Stop rule requires waiting for the user to provide the Stage 0-Implement prompt.",
  "last_updated": "2026-04-23"
}
STAGE_STATE_END

## Current Gate

Stage 0 planning is complete. No product implementation has started.

## Next Prompt

Use `[Stage 0-Implement]` from `Docs/frameproof_prompt_pack/prompts/stage0_implement.md`.

Do not proceed until the user provides the next prompt in a fresh `codex exec --ephemeral` session. Do not use `codex exec resume`.
