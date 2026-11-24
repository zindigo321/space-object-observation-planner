# 80-Second Demo Script

Preparation. Open this round's `demo_delivery/index.html`, select E3, seed17, baseline, and the initial plan, and keep the full-horizon view.

**0–15 seconds.** This is Team 2's autonomous observation planning demo. It uses real orbit data to show results that were already computed and validated. Each sample has 60 targets, three stations, and a one-day planning horizon. The page uses the smoke-test scoring rules. Full optical conditions remain unverified.

**15–30 seconds.** This is the seed17 baseline initial plan, with 180 points and 57 covered targets. Switch to the existing improved method to see 190 points with the same coverage and zero violations in the independent per-second check. Initial-plan gains for the three frozen seeds were 10.8, 10, and 10.8 points. Both methods used the same candidates and physical fault event.

Select the improved method. Then select the E4 late fault, baseline, and the fault impact view, and use the control that jumps to the time near the fault.

**30–55 seconds.** The late fault applies only to seed42. Station 2 fails for two hours starting at 01:03:03. The baseline already has 14 completed tasks. One in-progress task at a healthy station is locked, one task is interrupted, and two future tasks are affected. Cyan marks completed history, purple marks locked tasks, and orange marks the interrupted task, which scores zero. Gray and red show future tasks from the old plan.

Click a task to see its details, step forward once, and switch to the improved method.

**55–80 seconds.** Replanning preserves all history and avoids the fault. The baseline scores 172.4 and the improved method scores 184. Both cover 56 targets with zero violations. The improved method starts from a different initial plan, so the comparison applies to the complete workflows. The independent validator rejected deleted history and forged interruptions. The metrics come from this round's evidence, and the page supports offline playback, pause, and stepping.
