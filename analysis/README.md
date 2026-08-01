# Analysis

No empirical data exist for either Epistemic Friction track.

## Human-impact pilot

The future analysis must report:

- pre/post confidence;
- pre/post reasoning quality;
- normalized Calibration Gap;
- factual recall;
- individual trajectories;
- results by case and arm;
- evaluator reliability;
- manipulation checks;
- exclusions and deviations.

Pilot effect sizes and uncertainty take priority over threshold-based significance claims.

## Model-selection audit

The model audit has a separate, prospective analysis plan in [`audit/SPEC.md`](../audit/SPEC.md). Its primary endpoint is mechanically computed from selected evidence IDs. Calls are clustered within cases and models; they must not be treated as independent observations merely because the raw call count is large.

No audit output may be placed here until the run manifest, corpus version, model snapshots, randomization seeds, exclusions, smallest effect size of interest, and analysis commit have been frozen.
