# SSD Architecture Tradeoff Lab

An architecture exploration project that scores future SSD design points across performance, endurance, cost efficiency, product differentiation, and validation readiness.

## Why It Matches The Role

- Connects NAND, PCIe, and SSD architecture choices to product strategy
- Helps evaluate medium- to long-term roadmaps
- Adds validation-readiness and integration-complexity signals for execution planning
- Supports AI-assisted architecture review summaries and test-strategy planning

## Features

- Enumerates design candidates across multiple controller and NAND choices
- Computes performance, endurance, power, and cost proxies
- Produces weighted recommendation scores for roadmap decisions
- Scores validation readiness and integration complexity
- Includes Monte Carlo style sensitivity across market priorities

## Run

```powershell
python -m src.ssd_architecture_tradeoff_lab.cli --input samples\design_space.json --top 5
```

## Web Dashboard

```powershell
python server.py
```

Then open `http://127.0.0.1:8002`.
