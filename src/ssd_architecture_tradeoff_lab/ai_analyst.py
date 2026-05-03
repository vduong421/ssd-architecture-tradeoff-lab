from __future__ import annotations

import json
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parents[3] / "_shared_project_workbench"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

try:
    from local_llm import chat_json as _chat_json

    def chat_json(prompt, model="google/gemma-4-e4b"):
        # enforce correct LM Studio format
        return _chat_json(
            prompt=str(prompt),
            model=str(model)
        )

except Exception:
    def chat_json(prompt, model="google/gemma-4-e4b"):
        return {
            "answer": "Local LLM helper was not found.",
            "evidence": "Check _shared_project_workbench/local_llm.py import path.",
            "next_action": "Ensure shared workbench is accessible."
        }


PRIMARY_MODEL = "google/gemma-4-e4b"
FALLBACK_MODEL = "qwen3-14b"
# enforce LM Studio model naming


def deterministic_analyst_brief(result: dict) -> dict:
    top = result.get("top_candidates", [])
    if not top:
        return {
            "mode": "deterministic_fallback",
            "brief": "No candidates were generated.",
            "risk_flags": [],
            "next_steps": [],
            "resume_bullets": [],
        }

    leader = top[0]
    metrics = leader.get("metrics", {})
    risk_flags = []

    if leader.get("pcie_generation", 0) >= 6:
        risk_flags.append("PCIe Gen6 may increase signal-integrity, power, and validation complexity.")
    if leader.get("nand_type") == "QLC":
        risk_flags.append("QLC improves density but needs stronger endurance review.")
    if metrics.get("power_efficiency", 100) < 70:
        risk_flags.append("Power-efficiency is low enough to require thermal validation.")
    if leader.get("channels", 0) >= 16:
        risk_flags.append("High channel count improves bandwidth but increases controller and firmware validation scope.")

    if not risk_flags:
        risk_flags.append("No major deterministic risk flag triggered.")

    return {
        "mode": "deterministic_fallback",
        "brief": "This architecture is recommended because it gives the best weighted balance across SSD roadmap priorities.",
        "risk_flags": risk_flags,
        "next_steps": [
            "Run sensitivity analysis by changing performance, endurance, and cost weights.",
            "Compare the top two candidates and explain why the winner is stronger.",
            "Build validation tests around the weakest metric.",
        ],
        "resume_bullets": [
            "Built an SSD architecture tradeoff dashboard ranking candidates across performance, endurance, cost, power, and differentiation.",
            "Added a grounded AI analyst layer that converts deterministic scores into validation risks and next-step recommendations.",
            "Designed a local-first AI workflow using Gemma/Qwen fallback policy for private engineering analysis.",
        ],
    }


def generate_ai_analyst_brief(result: dict, model: str = PRIMARY_MODEL) -> dict:
    prompt = (
        "You are an SSD validation copilot.\n"
        "Use only the deterministic SSD architecture result below.\n"
        "Return ONLY valid JSON (no markdown) with keys: brief, risk_flags, next_steps, resume_bullets.\n\n"
        "Deterministic result:\n"
        + json.dumps(result, indent=2)
    )

    try:
        raw = chat_json(prompt, model=model)

        if isinstance(raw, dict):
            parsed = raw
        else:
            raw = str(raw).strip()
            start = raw.find("{")
            end = raw.rfind("}")
            parsed = json.loads(raw[start:end+1])

        return {
            "mode": "local_llm",
            "model": model,
            "ai_result": parsed,
        }

    except Exception as exc:
        fallback = deterministic_analyst_brief(result)
        fallback["local_model_status"] = f"Local model failed: {exc}"
        return fallback


def chat_about_project(question: str, result: dict, model: str = PRIMARY_MODEL) -> dict:
    prompt = (
        "You are a local AI project copilot for a resume portfolio project.\n"
        "Project: SSD Architecture Tradeoff Lab.\n"
        "Answer the user's question using only the deterministic project output below.\n"
        "Return ONLY valid JSON with keys: answer, evidence, next_action, recommendation, decision.\n\n"
        f"User question: {question}\n\n"
        "Project output:\n"
        + json.dumps(result, indent=2)
    )

    try:
        raw = chat_json(prompt, model=model)

        if isinstance(raw, dict):
            if "recommendation" not in raw:
                raw["recommendation"] = "Use deterministic scores as the source of truth and validate before production decisions."
            if "decision" not in raw:
                raw["decision"] = "Proceed with evidence-based design review."
            return raw

        if isinstance(raw, str):
            raw = raw.strip()
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                raw = raw[start:end+1]
            parsed = json.loads(raw)
            if "recommendation" not in parsed:
                parsed["recommendation"] = "Use deterministic scores as the source of truth and validate before production decisions."
            if "decision" not in parsed:
                parsed["decision"] = "Proceed with evidence-based design review."
            return parsed

        return {
            "answer": ["Unexpected response format from local AI."],
            "evidence": ["Non-JSON response"],
            "next_action": ["Check local_llm formatting."],
            "recommendation": ["Use deterministic fallback if local AI returns invalid content."],
            "decision": ["Do not trust unstructured AI output."]
        }

    except Exception as e:
        top = result.get("top_candidates", [])
        leader = top[0] if top else {}
        second = top[1] if len(top) >= 2 else {}
        summary = result.get("summary", {})
        q = question.lower()

        weakest_metric = summary.get("weakest_metric", "No weakest metric available.")
        recommended_theme = summary.get("recommended_theme", "No recommendation available.")

        if "risk" in q:
            answer = [
                "Differentiation is the weakest metric, indicating limited market uniqueness.",
                "PCIe Gen6 introduces higher signal integrity and validation complexity.",
                "High channel count increases firmware and controller validation scope."
            ]
            evidence = [
                f"Leader score: {leader.get('weighted_score', 0)}",
                f"Weakest metric: {weakest_metric}",
                f"Recommended architecture: {recommended_theme}"
            ]
            next_action = [
                "Validate PCIe Gen6 signal-integrity and power behavior.",
                "Improve differentiation through feature or architecture changes.",
                "Compare leader against the second candidate before final decision."
            ]
            recommendation = [
                "Use the top candidate as baseline.",
                "Prioritize improving weakest metric before scaling.",
                "Introduce validation gates before production decision."
            ]
            decision = [
                "Do not finalize design yet.",
                "Proceed to validation and architecture refinement stage."
            ]

        elif "root" in q or "weak" in q:
            answer = [
                f"Weakest metric identified: {weakest_metric}",
                "Design is overly optimized for performance over balance.",
                "Insufficient differentiation compared to alternative candidates."
            ]
            evidence = [
                f"Leader metrics: {leader.get('metrics', {})}",
                f"Architecture: PCIe Gen{leader.get('pcie_generation')}, {leader.get('channels')} channels, {leader.get('nand_type')} NAND"
            ]
            next_action = [
                "Analyze weakest metric contribution.",
                "Adjust architecture parameters incrementally.",
                "Re-run evaluation to measure improvement."
            ]
            recommendation = [
                "Balance performance with differentiation.",
                "Avoid over-optimization in one dimension.",
                "Use iterative evaluation cycles."
            ]
            decision = [
                "Hold current design.",
                "Refine weakest metric before proceeding."
            ]

        elif "tradeoff" in q or "compare" in q or "candidate" in q:
            answer = [
                f"Candidate 1 scores {leader.get('weighted_score', 0)}.",
                f"Candidate 2 scores {second.get('weighted_score', 0)}.",
                "The tradeoff is whether the small score gain is worth cost, power, and validation complexity."
            ]
            evidence = [
                f"Candidate 1: PCIe Gen{leader.get('pcie_generation')}, {leader.get('channels')} channels, {leader.get('nand_type')} NAND, {leader.get('dram_cache_gb')}GB DRAM",
                f"Candidate 2: PCIe Gen{second.get('pcie_generation')}, {second.get('channels')} channels, {second.get('nand_type')} NAND, {second.get('dram_cache_gb')}GB DRAM"
            ]
            next_action = [
                "Compare score gap between Candidate 1 and Candidate 2.",
                "Review whether the small score gain is worth cost, power, or validation complexity."
            ]
            recommendation = [
                "Use Candidate 1 only if the added roadmap value is worth implementation risk.",
                "Keep Candidate 2 as the lower-risk fallback option."
            ]
            decision = [
                "Shortlist Candidate 1 and Candidate 2 for design review."
            ]

        elif "action" in q or "next" in q or "recommend" in q:
            answer = [
                "Engineering should validate the top architecture.",
                "Engineering should compare it against the runner-up.",
                "Engineering should tune weights for customer priorities."
            ]
            evidence = [
                f"Candidate count: {result.get('candidate_count', 0)}",
                f"Best score: {summary.get('best_score', 0)}",
                f"Recommended theme: {recommended_theme}"
            ]
            next_action = [
                "Run sensitivity analysis on performance, endurance, cost, power, and differentiation weights.",
                "Create validation tests for the weakest metric.",
                "Prepare customer-facing explanation for the selected architecture."
            ]
            recommendation = [
                "Turn the deterministic ranking into a design-review workflow with risk gates.",
                "Use AI to explain results, not replace deterministic scoring."
            ]
            decision = [
                "Proceed with top-candidate validation planning."
            ]

        else:
            answer = [
                f"Top candidate has highest weighted score: {leader.get('weighted_score', 0)}.",
                "It is balanced across performance, endurance, and cost.",
                "It was selected based on the deterministic evaluation model."
            ]
            evidence = [
                f"Recommended theme: {recommended_theme}",
                f"Weakest metric: {weakest_metric}"
            ]
            next_action = [
                "Validate top candidate performance.",
                "Compare against runner-up design.",
                "Review weakest metric impact."
            ]
            recommendation = [
                "Use deterministic results as baseline.",
                "Apply AI only as explanation layer.",
                "Validate before production decisions."
            ]
            decision = [
                "Proceed with structured design review.",
                "Do not finalize without validation."
            ]

        return {
            "answer": answer,
            "evidence": evidence,
            "next_action": next_action,
            "recommendation": recommendation,
            "decision": decision,
            "risks": evidence,
            "operator_actions": next_action,
            "local_model_status": f"Fallback used because local AI failed: {e}"
        }