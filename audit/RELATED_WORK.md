# Related-work boundary

This note positions the prospective audit using a preliminary search current to 2026-07-31. It is not a systematic literature review and must be expanded before preregistration or paper submission.

## Foundations

- [Discovering Language Model Behaviors with Model-Written Evaluations](https://arxiv.org/abs/2212.09251) (Perez et al., 2022/2023) introduced model-written evaluations that include matching a dialogue user's stated preference.
- [Towards Understanding Sycophancy in Language Models](https://arxiv.org/abs/2310.13548) (Sharma et al., 2023) studies belief-matching across free-form generation tasks and the role of human preference data.
- [Question Decomposition Improves the Faithfulness of Model-Generated Reasoning](https://arxiv.org/abs/2307.11768) (Radhakrishnan et al., 2023) reports that factored decomposition can mitigate sycophancy, making decomposition an important antecedent to the proposed stage separation.

## Closest overlaps and boundary

- [What Counts as AI Sycophancy? A Taxonomy and Expert Survey of a Fragmented Construct](https://arxiv.org/abs/2605.21778) maps 70 papers and identifies framing, omission, and selective evidence as comparatively under-studied implicit behavior.
- [Evaluating Evidence Grounding Under User Pressure in Instruction-Tuned Language Models](https://arxiv.org/abs/2603.20162) holds in-context evidence fixed and measures pressure-induced judgment shifts, while explicitly leaving retrieval and evidence-selection failures outside its scope.
- [From Sycophancy to Deception: A Unified Taxonomy for LLM Spontaneous Misalignment](https://arxiv.org/abs/2604.04788) reports that omission and pragmatic distortion remain under-covered relative to fabrication.
- [Beyond Semantic Relevance: Counterfactual Risk Minimization for Robust Retrieval-Augmented Generation](https://arxiv.org/abs/2605.01302) proposes a robustness-oriented evidence critic for biased queries.

## Intended distinction

Epistemic Friction does not claim to discover sycophancy. Its proposed contribution is a paired black-box audit of stance-conditioned selection from one registered dossier, using mechanical evidence IDs, a user-versus-third-party control, and a stance-blind selection mitigation.

The fixed-evidence user-pressure study is the closest identified overlap. The proposed incremental contribution is not another judgment-shift result: it is a registered, mechanically scored selection endpoint; a requester-versus-third-party control; independent order, ID, and option-label counterbalancing; and a stance-blind selection mitigation.

That distinction is provisional and must survive a documented, reproducible literature search before preregistration or submission.
