"""Structural core-candidate ranking for schematic analysis."""

from __future__ import annotations

from dataclasses import dataclass

from .component_rules import get_net_names


@dataclass
class CoreCandidate:
    """One structurally ranked component candidate."""

    instance_id: str
    sheet_instance_path: str
    reference: str
    value: str
    lib_id: str
    score: int
    priority: int
    pin_count: int
    net_count: int
    sheet_centrality: int = 0
    rail_fanout: int = 0


def _normalize_sheet_instance_path(sheet_instance_path: str | None) -> str:
    normalized = str(sheet_instance_path or "").strip().rstrip("/")
    return normalized or "/"


def _build_instance_id(reference: str, sheet_instance_path: str) -> str:
    ref = str(reference or "").upper()
    if not ref:
        return ""
    if sheet_instance_path in {"", "/"}:
        return f"/{ref}"
    return f"{sheet_instance_path}/{ref}"


def calculate_structural_score(component: dict[str, Any], rule_paths: tuple[str, ...] = ()) -> int:
    """Calculate a core score from structural evidence only."""
    del rule_paths

    pin_count = len(component.get("pins", []))
    net_count = len(set(get_net_names(component)))
    return pin_count + net_count


def rank_core_candidates(
    components: list[dict[str, Any]],
    top_n: int = 5,
    rule_paths: tuple[str, ...] = (),
) -> list[CoreCandidate]:
    """Rank structurally important components without role inference."""
    del rule_paths
    candidates: list[CoreCandidate] = []

    for component in components:
        reference = str(component.get("reference", "")).upper()
        if not reference:
            continue

        # Skip DNP components — they are not populated on the board
        flags = component.get("flags", {})
        if isinstance(flags, dict) and flags.get("dnp"):
            continue

        score = calculate_structural_score(component)
        if score <= 0:
            continue

        sheet_instance_path = _normalize_sheet_instance_path(component.get("sheet_instance_path"))
        instance_id = str(component.get("instance_id") or _build_instance_id(reference, sheet_instance_path))
        candidates.append(
            CoreCandidate(
                instance_id=instance_id,
                sheet_instance_path=sheet_instance_path,
                reference=reference,
                value=str(component.get("value", "")),
                lib_id=str(component.get("lib_id", "")),
                score=score,
                priority=0,
                pin_count=len(component.get("pins", [])),
                net_count=len(set(get_net_names(component))),
            )
        )

    candidates.sort(
        key=lambda candidate: (
            candidate.score,
            candidate.net_count,
            candidate.pin_count,
            candidate.reference,
        ),
        reverse=True,
    )

    for priority, candidate in enumerate(candidates[:top_n], start=1):
        candidate.priority = priority

    return candidates[:top_n]
