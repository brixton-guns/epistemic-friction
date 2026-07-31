from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from epistemic_friction.audit import AuditValidationError, validate_audit_assets

REQUIRED_ARMS = {"continuity", "neutral", "friction", "static_neutral"}
EXPECTED_RATIOS = {
    "continuity": (0.70, 0.30),
    "neutral": (0.50, 0.50),
    "friction": (0.30, 0.70),
    "static_neutral": (0.50, 0.50),
}
TOLERANCE = 1e-9
MANIFEST_EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "build",
    "dist",
}


class ValidationError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_scope_files(root: Path, manifest_path: Path) -> set[str]:
    """Return source artifacts covered by the integrity manifest."""
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
        and path != manifest_path
        and path.name != ".DS_Store"
        and not any(
            part in MANIFEST_EXCLUDED_DIRS or part.endswith(".egg-info")
            for part in path.parts
        )
    }


def validate_registry(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    facts = registry.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ValidationError("registry.facts must be a non-empty list")

    by_id: dict[str, dict[str, Any]] = {}
    totals = {"A": 0, "B": 0}

    for fact in facts:
        required = {
            "id", "direction", "text", "relevance", "strength",
            "weight", "dimension", "interpretation"
        }
        missing = required - set(fact)
        if missing:
            raise ValidationError(
                f"fact {fact.get('id', '<unknown>')} missing fields: {sorted(missing)}"
            )

        fact_id = fact["id"]
        if fact_id in by_id:
            raise ValidationError(f"duplicate fact id: {fact_id}")
        if fact["direction"] not in {"A", "B"}:
            raise ValidationError(f"{fact_id}: direction must be A or B")
        if not isinstance(fact["text"], str) or not fact["text"].strip():
            raise ValidationError(f"{fact_id}: text must be non-empty")
        if fact["relevance"] not in {1, 2, 3, 4}:
            raise ValidationError(f"{fact_id}: relevance must be 1..4")
        if fact["strength"] not in {1, 2, 3, 4}:
            raise ValidationError(f"{fact_id}: strength must be 1..4")

        computed = fact["relevance"] * fact["strength"]
        if fact["weight"] != computed:
            raise ValidationError(
                f"{fact_id}: weight={fact['weight']} but relevance×strength={computed}"
            )

        totals[fact["direction"]] += fact["weight"]
        by_id[fact_id] = fact

    if totals["A"] != totals["B"]:
        raise ValidationError(
            f"registry is unbalanced: A={totals['A']} B={totals['B']}"
        )

    return by_id


def _side_for(initial_choice: str, fact_direction: str) -> str:
    return "support" if initial_choice == fact_direction else "oppose"


def validate_plans(
    plans: dict[str, Any],
    facts: dict[str, dict[str, Any]],
) -> list[str]:
    messages: list[str] = []
    choices = plans.get("initial_choices")
    if set(choices or {}) != {"A", "B"}:
        raise ValidationError("plans must define initial choices A and B")

    for initial_choice in ("A", "B"):
        arms = choices[initial_choice]
        if set(arms) != REQUIRED_ARMS:
            raise ValidationError(
                f"{initial_choice}: arms must be exactly {sorted(REQUIRED_ARMS)}"
            )

        for arm, plan in arms.items():
            ids = plan.get("fact_ids")
            if not isinstance(ids, list) or not ids:
                raise ValidationError(f"{initial_choice}/{arm}: fact_ids must be non-empty")
            if len(ids) != len(set(ids)):
                raise ValidationError(f"{initial_choice}/{arm}: duplicate Fact ID")

            support = 0
            oppose = 0
            for fact_id in ids:
                if fact_id not in facts:
                    raise ValidationError(
                        f"{initial_choice}/{arm}: unknown Fact ID {fact_id}"
                    )
                fact = facts[fact_id]
                side = _side_for(initial_choice, fact["direction"])
                if side == "support":
                    support += fact["weight"]
                else:
                    oppose += fact["weight"]

            total = support + oppose
            if total <= 0:
                raise ValidationError(f"{initial_choice}/{arm}: zero evidence weight")

            actual = (support / total, oppose / total)
            expected = EXPECTED_RATIOS[arm]
            if abs(actual[0] - expected[0]) > TOLERANCE:
                raise ValidationError(
                    f"{initial_choice}/{arm}: ratio "
                    f"{actual[0]:.2f}/{actual[1]:.2f}, expected "
                    f"{expected[0]:.2f}/{expected[1]:.2f}"
                )

            declared = plan.get("declared_weight")
            if declared != {"support": support, "oppose": oppose}:
                raise ValidationError(
                    f"{initial_choice}/{arm}: declared weights do not match computed weights"
                )

            messages.append(
                f"{initial_choice}/{arm}: PASS "
                f"({support}:{oppose}, {actual[0]:.0%}/{actual[1]:.0%})"
            )

    return messages


def verify_manifest(root: Path) -> list[str]:
    manifest_path = root / "integrity" / "manifest.json"
    manifest = read_json(manifest_path)
    entries = manifest.get("files")
    if not isinstance(entries, dict) or not entries:
        raise ValidationError("integrity manifest has no files")

    expected_files = manifest_scope_files(root, manifest_path)
    missing_entries = sorted(expected_files - set(entries))
    stale_entries = sorted(set(entries) - expected_files)
    if missing_entries or stale_entries:
        details: list[str] = []
        if missing_entries:
            details.append("unhashed files: " + ", ".join(missing_entries))
        if stale_entries:
            details.append("stale manifest entries: " + ", ".join(stale_entries))
        raise ValidationError("manifest scope mismatch\n" + "\n".join(details))

    messages: list[str] = []
    for relative, expected in sorted(entries.items()):
        path = root / relative
        if not path.is_file():
            raise ValidationError(f"manifest file missing: {relative}")
        actual = sha256(path)
        if actual != expected:
            raise ValidationError(
                f"hash mismatch: {relative}\nexpected {expected}\nactual   {actual}"
            )
        messages.append(f"integrity/{relative}: PASS")
    return messages


def run_validation(root: Path | None = None) -> list[str]:
    root = root or repository_root()
    registry_path = root / "cases" / "case-001-transit" / "fact_registry.json"
    plans_path = root / "cases" / "case-001-transit" / "condition_plans.json"

    registry = read_json(registry_path)
    facts = validate_registry(registry)
    plans = read_json(plans_path)
    messages = [
        f"registry: PASS ({len(facts)} facts, balanced total weight)",
        *validate_plans(plans, facts),
        *validate_audit_assets(root),
        *verify_manifest(root),
    ]
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Epistemic Friction protocols")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (defaults to installed source repository)",
    )
    args = parser.parse_args()

    try:
        messages = run_validation(args.root)
    except (ValidationError, AuditValidationError) as exc:
        print(f"EPISTEMIC FRICTION VALIDATION: FAIL\n{exc}")
        return 1

    print("EPISTEMIC FRICTION VALIDATION: PASS")
    for message in messages:
        print(f"- {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
