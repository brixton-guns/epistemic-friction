from __future__ import annotations

import json
import unittest
from pathlib import Path

from epistemic_friction.audit import (
    AuditValidationError,
    REQUIRED_ARMS,
    compute_assessment_endpoint,
    compute_primary_endpoint,
    public_render_bundle,
    render_block,
    render_synthesis_request,
    score_selection,
    validate_audit_assets,
    validate_protocol,
    validate_selection_output,
    validate_synthesis_output,
)


class ModelSelectionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.protocol = json.loads(
            (cls.root / "audit" / "protocol.json").read_text(encoding="utf-8")
        )

    def test_audit_assets_pass(self) -> None:
        messages = validate_audit_assets(self.root)
        self.assertTrue(any("five-arm confound control: PASS" in message for message in messages))
        self.assertTrue(any("audit renderer: PASS" in message for message in messages))

    def test_protocol_has_one_primary_endpoint(self) -> None:
        validate_protocol(self.protocol)
        self.assertEqual(
            self.protocol["primary_endpoint"],
            "user_specific_selection_shift",
        )
        self.assertFalse(self.protocol["analysis"]["raw_calls_are_independent"])

    def test_user_and_third_party_pairs_are_mirrored(self) -> None:
        arms = self.protocol["arms"]
        normalize = lambda value: value.replace("Option A", "Option X").replace(
            "Option B", "Option X"
        )
        self.assertEqual(
            normalize(arms["user_a"]["statement"]),
            normalize(arms["user_b"]["statement"]),
        )
        self.assertEqual(
            normalize(arms["third_party_a"]["statement"]),
            normalize(arms["third_party_b"]["statement"]),
        )

    def test_user_and_third_party_templates_differ_only_by_source(self) -> None:
        arms = self.protocol["arms"]
        source = lambda value: value.split(". ", maxsplit=1)[1]
        self.assertEqual(
            source(arms["user_a"]["statement"]),
            source(arms["third_party_a"]["statement"]),
        )

    def test_all_arms_share_one_prefix_and_mapping_within_block(self) -> None:
        bundle = render_block(root=self.root, block_index=0, swap_options=False)
        self.assertEqual(set(bundle["arms"]), REQUIRED_ARMS)
        prefix = bundle["common_user_prefix"]
        for arm in bundle["arms"].values():
            self.assertTrue(arm["prompt"].startswith(prefix))
            self.assertTrue(arm["prompt"].endswith(arm["statement"]))
        self.assertEqual(len(bundle["hidden_mapping"]), 16)

    def test_registered_ids_never_leak_into_prompt(self) -> None:
        bundle = render_block(root=self.root, block_index=0, swap_options=False)
        prompt = bundle["common_user_prefix"]
        for entry in bundle["hidden_mapping"]:
            self.assertNotIn(entry["registered_fact_id"], prompt)

    def test_human_pilot_instructions_never_leak_into_audit_prompt(self) -> None:
        bundle = render_block(root=self.root, block_index=0, swap_options=False)
        prompt = bundle["common_user_prefix"].lower()
        self.assertNotIn("participant task", prompt)
        self.assertNotIn("before and after the intervention", prompt)
        self.assertNotIn("confidence from 0 to 100", prompt)

    def test_mapping_changes_between_blocks(self) -> None:
        first = render_block(root=self.root, block_index=0, swap_options=False)
        second = render_block(root=self.root, block_index=1, swap_options=False)
        first_ids = [entry["registered_fact_id"] for entry in first["hidden_mapping"]]
        second_ids = [entry["registered_fact_id"] for entry in second["hidden_mapping"]]
        self.assertNotEqual(first_ids, second_ids)

    def test_option_label_swap_reverses_displayed_not_registered_direction(self) -> None:
        original = render_block(root=self.root, block_index=0, swap_options=False)
        swapped = render_block(root=self.root, block_index=0, swap_options=True)
        original_by_fact = {
            entry["registered_fact_id"]: entry for entry in original["hidden_mapping"]
        }
        swapped_by_fact = {
            entry["registered_fact_id"]: entry for entry in swapped["hidden_mapping"]
        }
        self.assertEqual(set(original_by_fact), set(swapped_by_fact))
        for fact_id, original_entry in original_by_fact.items():
            swapped_entry = swapped_by_fact[fact_id]
            self.assertEqual(original_entry["display_id"], swapped_entry["display_id"])
            self.assertEqual(
                original_entry["registered_direction"],
                swapped_entry["registered_direction"],
            )
            self.assertNotEqual(
                original_entry["display_direction"],
                swapped_entry["display_direction"],
            )

    def test_display_ids_are_not_position_numbers(self) -> None:
        bundle = render_block(root=self.root, block_index=0, swap_options=False)
        displayed_ids = [entry["display_id"] for entry in bundle["hidden_mapping"]]
        positional_ids = [f"E{index:02d}" for index in range(1, len(displayed_ids) + 1)]
        self.assertNotEqual(displayed_ids, positional_ids)

    def test_option_labels_are_exactly_counterbalanced_within_case(self) -> None:
        blocks = len(self.protocol["randomization"]["pilot_block_seeds"])
        swaps = [
            render_block(root=self.root, block_index=index)["swap_options"]
            for index in range(blocks)
        ]
        self.assertEqual(swaps.count(True), swaps.count(False))

    def test_selection_schema_matches_registered_selection_size(self) -> None:
        schema = json.loads(
            (self.root / "audit" / "schemas" / "selection_output.schema.json").read_text(
                encoding="utf-8"
            )
        )
        selection = schema["properties"]["selected_evidence"]
        self.assertEqual(selection["minItems"], self.protocol["selection_size"])
        self.assertEqual(selection["maxItems"], self.protocol["selection_size"])
        self.assertTrue(selection["uniqueItems"])

    def test_selection_scoring_uses_hidden_registered_mapping(self) -> None:
        bundle = render_block(root=self.root, block_index=0, swap_options=False)
        a_ids = [
            entry["display_id"]
            for entry in bundle["hidden_mapping"]
            if entry["display_direction"] == "A"
        ][:3]
        b_id = next(
            entry["display_id"]
            for entry in bundle["hidden_mapping"]
            if entry["display_direction"] == "B"
        )
        score = score_selection({"selected_evidence": a_ids + [b_id]}, bundle)
        self.assertEqual(score["selected_count_a"], 3)
        self.assertEqual(score["selected_count_b"], 1)
        self.assertEqual(score["selected_share_a"], 0.75)

    def test_invalid_selection_is_rejected_without_repair(self) -> None:
        bundle = render_block(root=self.root, block_index=0, swap_options=False)
        with self.assertRaises(AuditValidationError):
            validate_selection_output(
                {"selected_evidence": ["E01", "E01", "E02", "E99"]},
                bundle,
            )

    def test_primary_endpoint_is_mechanical_difference_in_differences(self) -> None:
        endpoint = compute_primary_endpoint(
            {
                "user_a": {"selected_count_a": 4},
                "user_b": {"selected_count_a": 1},
                "third_party_a": {"selected_count_a": 3},
                "third_party_b": {"selected_count_a": 2},
            },
            selection_size=4,
        )
        self.assertEqual(endpoint["user_directional_shift"], 0.75)
        self.assertEqual(endpoint["third_party_directional_shift"], 0.25)
        self.assertEqual(endpoint["user_specific_selection_shift"], 0.5)

    def test_public_bundle_omits_private_scoring_ledger(self) -> None:
        bundle = render_block(root=self.root, block_index=0)
        public = public_render_bundle(bundle)
        self.assertNotIn("hidden_mapping", public)
        self.assertIn("private_ledger_sha256", public)

    def test_synthesis_renderer_enforces_pipeline_exposure(self) -> None:
        bundle = render_block(root=self.root, block_index=0)
        selection = {
            "selected_evidence": [
                item["display_id"]
                for item in reversed(bundle["displayed_evidence"][:4])
            ]
        }
        direct = render_synthesis_request(
            bundle,
            selection,
            arm_name="user_a",
            pipeline_name="direct",
            selector_arm="user_a",
            root=self.root,
        )
        blind = render_synthesis_request(
            bundle,
            selection,
            arm_name="user_a",
            pipeline_name="blind_selection",
            selector_arm="neutral",
            root=self.root,
        )
        fully_blind = render_synthesis_request(
            bundle,
            selection,
            arm_name="user_a",
            pipeline_name="fully_blind",
            selector_arm="neutral",
            root=self.root,
        )
        canonical = [item["display_id"] for item in bundle["displayed_evidence"][:4]]
        self.assertEqual(direct["canonical_selected_evidence"], canonical)
        self.assertEqual(direct["synthesizer_stance_arm"], "user_a")
        self.assertEqual(blind["synthesizer_stance_arm"], "user_a")
        self.assertEqual(fully_blind["synthesizer_stance_arm"], "neutral")

    def test_synthesis_renderer_rejects_wrong_selector_arm(self) -> None:
        bundle = render_block(root=self.root, block_index=0)
        selection = {
            "selected_evidence": [
                item["display_id"] for item in bundle["displayed_evidence"][:4]
            ]
        }
        with self.assertRaises(AuditValidationError):
            render_synthesis_request(
                bundle,
                selection,
                arm_name="user_a",
                pipeline_name="blind_selection",
                selector_arm="user_a",
                root=self.root,
            )

    def test_numeric_synthesis_endpoint_is_validated_and_scored(self) -> None:
        outputs = {
            "user_a": {"decision": "A", "assessment_option_a": 80},
            "user_b": {"decision": "B", "assessment_option_a": 40},
            "third_party_a": {"decision": "A", "assessment_option_a": 65},
            "third_party_b": {"decision": "B", "assessment_option_a": 45},
        }
        endpoint = compute_assessment_endpoint(outputs)
        self.assertAlmostEqual(endpoint["user_assessment_shift"], 0.4)
        self.assertAlmostEqual(endpoint["third_party_assessment_shift"], 0.2)
        self.assertAlmostEqual(endpoint["user_specific_assessment_shift"], 0.2)
        with self.assertRaises(AuditValidationError):
            validate_synthesis_output(
                {"decision": "A", "assessment_option_a": 101}
            )


if __name__ == "__main__":
    unittest.main()
