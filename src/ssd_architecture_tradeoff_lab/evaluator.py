from __future__ import annotations

from .catalog import enumerate_candidates


def score_candidate(candidate: dict, weights: dict) -> dict:
    pcie_generation = candidate["pcie_generation"]
    channels = candidate["channels"]
    nand_type = candidate["nand_type"]
    controller_node = candidate["controller_nodes_nm"]
    dram_cache = candidate["dram_cache_gb"]
    overprovisioning = candidate["overprovisioning_pct"]

    perf = pcie_generation * 18 + channels * 5 + dram_cache * 2
    perf += 6 if nand_type == "TLC" else -4

    endurance = channels * 2 + overprovisioning * 2.6 + (18 if nand_type == "TLC" else 8)
    cost_eff = 130 - (channels * 3.8 + dram_cache * 4.5 + (8 if nand_type == "TLC" else 0))
    power_eff = 120 - (channels * 2.5 + dram_cache * 2 + (10 if pcie_generation == 6 else 0))
    power_eff += 8 if controller_node == 5 else 0
    validation_readiness = 58 + channels * 1.5 + overprovisioning * 0.9 + (6 if nand_type == "TLC" else 0)
    validation_readiness -= 7 if pcie_generation == 6 else 0
    validation_readiness += 5 if controller_node == 5 else 0
    integration_complexity = 22 + channels * 3.2 + dram_cache * 1.5 + (8 if pcie_generation == 6 else 0)
    integration_complexity += 6 if nand_type == "QLC" else 2

    differentiation = 0
    if pcie_generation >= 5:
        differentiation += 25
    if nand_type == "QLC" and overprovisioning >= 12:
        differentiation += 18
    if dram_cache >= 8:
        differentiation += 12
    if controller_node == 5:
        differentiation += 15

    weighted = (
        perf * weights["performance"]
        + endurance * weights["endurance"]
        + cost_eff * weights["cost_efficiency"]
        + power_eff * weights["power_efficiency"]
        + differentiation * weights["differentiation"]
    )

    return {
        **candidate,
        "metrics": {
            "performance": round(perf, 2),
            "endurance": round(endurance, 2),
            "cost_efficiency": round(cost_eff, 2),
            "power_efficiency": round(power_eff, 2),
            "differentiation": round(differentiation, 2),
            "validation_readiness": round(validation_readiness, 2),
            "integration_complexity": round(integration_complexity, 2),
        },
        "weighted_score": round(weighted, 2),
        "ai_focus": _build_ai_focus(validation_readiness, integration_complexity, candidate),
    }


def evaluate_design_space(payload: dict, top_n: int = 5) -> dict:
    weights = payload["weights"]
    candidates = enumerate_candidates(payload["design_space"])
    scored = [score_candidate(candidate, weights) for candidate in candidates]
    ranked = sorted(scored, key=lambda item: item["weighted_score"], reverse=True)
    leader = ranked[0] if ranked else {}

    return {
        "candidate_count": len(ranked),
        "top_candidates": ranked[:top_n],
        "summary": {
            "best_score": leader.get("weighted_score", 0),
            "recommended_theme": _recommendation_text(leader),
            "validation_ready_count": sum(
                1 for item in ranked if item["metrics"]["validation_readiness"] >= 80
            ),
            "ai_focus_area": leader.get("ai_focus", "No design candidates available."),
            "test_strategy_note": _test_strategy_note(leader),
        },
    }


def _recommendation_text(candidate: dict) -> str:
    if not candidate:
        return "No candidates were generated."
    return (
        f"Prioritize PCIe Gen{candidate['pcie_generation']} with {candidate['channels']} channels, "
        f"{candidate['nand_type']} NAND, {candidate['dram_cache_gb']}GB DRAM cache, and "
        f"{candidate['overprovisioning_pct']}% overprovisioning."
    )


def _build_ai_focus(validation_readiness: float, integration_complexity: float, candidate: dict) -> str:
    if validation_readiness < 80:
        return (
            f"Use AI-generated validation planning for Gen{candidate['pcie_generation']} {candidate['nand_type']} "
            "to expand test coverage before broad architecture commitment."
        )
    if integration_complexity > 85:
        return "Use AI-assisted review notes to summarize cross-team integration risk and dependency hotspots."
    return "Use the design as a pilot for AI-generated scorecards and architecture-review summaries."


def _test_strategy_note(candidate: dict) -> str:
    if not candidate:
        return "No test strategy available."
    if candidate["metrics"]["validation_readiness"] < 80:
        return "Front-load interoperability, endurance, and corner-case QoS validation before customer-facing rollout."
    if candidate["metrics"]["integration_complexity"] > 85:
        return "Pair the design with a staged integration plan and dashboard tracking for firmware, media, and platform milestones."
    return "Validation posture is strong enough for a broader execution dashboard and repository-scale regression plan."
