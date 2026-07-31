# Epistemic Friction
## Conversational Inertia and Epistemic Calibration
### Pilot Specification v0.1 — First Stone

**Status:** preregistered design draft  
**Study type:** exploratory randomized controlled pilot  
**Primary object:** confidence growth relative to reasoning-quality growth  
**Evidence status:** no empirical evidence has yet been collected

---

## 1. Research question

Does an assistant that preferentially develops a user's initial position increase confidence more than it improves the quality of the user's reasons?

The study does not assume intention, manipulation, self-awareness, or privileged model introspection. The proposed mechanism is conversational inertia: a system optimized to continue an exchange smoothly may extend the frame already present instead of interrupting it.

## 2. Core hypothesis

At equal factual accuracy and controlled informational volume, a Continuity condition will produce a larger normalized increase in confidence than in reasoning quality, compared with a Neutral conversational condition.

Primary outcome:

```text
Calibration Gap =
normalized change in confidence
-
normalized change in reasoning quality
```

A positive value means confidence increased more than measured reasoning quality.

## 3. Primary comparison

Conversational Continuity versus Conversational Neutral.

The hypothesis is not supported merely because confidence rises. Confidence may rise legitimately when reasons improve.

## 4. Experimental arms

### A. Conversational Continuity

Evidence weight follows the participant's initial choice at a 70/30 ratio.

### B. Conversational Neutral

Evidence weight is split 50/50.

### C. Conversational Friction

Evidence weight opposes the participant's initial choice at a 30/70 ratio.

### D. Static Neutral

The same balanced evidence policy as Neutral, delivered without dialogue.

The pilot does not fully separate selection, dialogue, and personalization. A later confirmatory study may use a complete 2 × 3 design.

## 5. Manipulation rule

The independent variable is registered evidence selection, not personality or tone.

Each fact has:

- a stable ID;
- exact wording;
- direction;
- relevance;
- evidential strength;
- computed weight;
- decision dimension;
- permitted interpretation.

Evidence plans are balanced by total weight, not merely by fact count.

The model may phrase registered facts but may not:

- invent evidence;
- alter numbers;
- import external facts;
- omit required Fact IDs;
- change the registered evidence ratio;
- use praise or hostility as the manipulation.

## 6. Primary measures

Before and after intervention, participants report:

- choice;
- confidence from 0 to 100;
- justification;
- relevant facts;
- strongest opposing argument;
- evidence that would cause revision.

Reasoning quality is scored from 0 to 16 across:

1. relevant fact use;
2. counterevidence integration;
3. strong reconstruction of the opposing argument;
4. concrete revision conditions.

Scores are normalized before calculating the Calibration Gap.

## 7. Human evaluation

At least two evaluators score anonymized responses while blind to:

- experimental arm;
- participant identity;
- confidence scores;
- assistant output;
- study hypothesis where practical.

Inter-rater reliability must be reported. If total-score reliability is below 0.65, the reasoning measure is treated as unstable and the pilot must be redesigned.

## 8. Pilot sample

Target: 48 participants, 12 per arm.  
Permitted range: 40–60.

The pilot estimates variance, manipulation quality, fatigue, rubric reliability, and case dependence. It is not confirmatory.

## 9. Criteria that weaken or kill the hypothesis

The hypothesis is weakened if:

- Continuity does not exceed Neutral in Calibration Gap in at least two of three cases;
- confidence and reasoning quality rise proportionally;
- the pooled effect disappears after controlling for factual recall;
- the result depends on one case;
- tone, length, factual accuracy, or evidence strength differ across arms;
- evaluator reliability is inadequate;
- Static Neutral matches or exceeds Continuity;
- a larger confirmatory study fails to reproduce the effect.

Null and contradictory results must be published.

## 10. Interpretation of Friction

Lower confidence alone is not success.

Possible outcomes:

- productive friction: calibration and reasoning improve;
- empty friction: confidence falls, reasons do not improve;
- harmful friction: comprehension or recall worsens;
- defensive friction: commitment hardens.

The study does not assume that contradiction is a cure.

## 11. First Stone acceptance gates

The First Stone passes only if:

1. the Fact Registry is structurally valid;
2. directions and weights are valid;
3. total registered weight is balanced between A and B;
4. every evidence plan references existing facts;
5. every plan has the registered ratio;
6. all required arms exist for both possible initial choices;
7. no evidence plan duplicates a Fact ID;
8. integrity hashes match;
9. automated tests pass;
10. deliberate tampering is detected.

## 12. Stop rule

After participant data become visible, no arm, outcome, hypothesis, or case may be added silently. Any change must be versioned, justified, prospective, and labeled exploratory where necessary.

## 13. Final standard

Epistemic Friction must distinguish among:

- a hypothesis becoming more elegant;
- a hypothesis becoming harder to criticize;
- a hypothesis receiving empirical support.

Only the third counts as evidence.

Epistemic Friction is designed to give its own central claim a fair opportunity to fail.
