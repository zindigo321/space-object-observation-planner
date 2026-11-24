# Optional Legacy Evaluator (Blocked and Isolated)

The original entry point remains in the local ignored paths `prototype_v1/evaluate/` and `prototype_v1/evaluator_adapter.py`, outside the current main workflow.

The independent audit on 2026-10-21 found that the SHA-256 hashes of `PLAN.md` and `EXECUTION_REQUIREMENTS.md` bound by the legacy evaluator differed from the downloaded copies. The adapter's `earliest_midpoint_prioritize_future` event-selection rule was also outside its allowed set. The local evidence is in `outputs/prior_audit/optional_evaluator_gate.json`. This round inspected the evidence and implementation and retained the historical `BLOCKED` status.

Running `python smoke_test.py --optional-evaluator --out outputs/optional_check_01` explicitly reports `BLOCKED` and returns 3. It bypasses the legacy entry point and preserves the hash checks. The main validator completes this round's evaluation independently.

To restore the optional evaluator, first confirm the actual rules version, recheck file hashes, and implement the real event-selection semantics. Then run traceable compatibility tests. A rename does not establish equivalent rules. This work remains pending and did not block the baseline handoff.
