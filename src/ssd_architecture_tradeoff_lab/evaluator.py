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
        },
        "weighted_score": round(weighted, 2),
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

