# Epistemic Friction

**Protocols for evidence selection, conversational inertia, and epistemic calibration**

Epistemic Friction is a protocol repository. It is not a paper, a completed study, or evidence that its hypotheses are true.

The repository now contains two linked but causally distinct tracks:

| Track | Intervention | Measured object | Status |
|---|---|---|---|
| [Human-impact pilot](SPEC.md) | The experimenter fixes the evidence bundle shown to a participant | Confidence growth relative to reasoning-quality growth | First Stone v0.1.1; one synthetic case; not recruitment-ready |
| [Model-selection audit](audit/SPEC.md) | The evidence dossier stays fixed while the attributed stance changes | Which registered evidence a model selects, followed by its verdict | Protocol v0.2.0; no model calls or results |

Keeping the tracks separate prevents a central category error: the human pilot studies the effect of controlled evidence exposure, while the model audit studies whether a model itself changes evidence selection under a stance cue.

## What is already real

- one complete synthetic decision case;
- a balanced, machine-readable Fact Registry;
- deterministic evidence plans for the human-impact pilot:
  - Continuity: 70/30;
  - Neutral: 50/50;
  - Friction: 30/70;
  - Static Neutral: 50/50;
- a five-arm, paired model-audit protocol with explicit impartiality controls;
- deterministic per-block evidence shuffling and opaque display IDs;
- independent ID permutation and exact within-case A/B label counterbalancing;
- machine-readable selection and synthesis output schemas;
- mechanical selection validation, scoring, and primary-endpoint computation;
- an auditable validation command and integrity manifest;
- automated tests, including tamper detection.

## Run

Requires Python 3.11 or newer.

```bash
python -m pip install -e .
epistemic-friction-validate
epistemic-friction-render-audit --block-index 0
python -m unittest discover -s tests -v
```

Without installation:

```bash
PYTHONPATH=src python -m epistemic_friction.validate
PYTHONPATH=src python -m epistemic_friction.audit --block-index 0
PYTHONPATH=src python -m unittest discover -s tests -v
```

The renderer omits the private Fact-ID/direction ledger by default. Use `--include-private-ledger` only to create a separately protected scoring ledger; never send that output to a model.

## Current boundary

The code validates and renders experimental materials. It does **not** yet:

- call a language model;
- recruit or manage participants;
- score human responses;
- establish that user stance changes model evidence selection;
- establish that conversational inertia exists.

The integrity manifest proves only that registered files have not changed relative to the current manifest. It is not a substitute for an external, timestamped preregistration.

The next milestone is a no-cost dry run of the audit renderer, followed by construction and blind annotation of enough cases for the registered pilot. No API run should begin before the pilot corpus, model list, analysis code, exclusion rules, and run manifest are frozen.
