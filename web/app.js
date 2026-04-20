const runButton = document.getElementById("runButton");
const runStatus = document.getElementById("runStatus");
const candidateCount = document.getElementById("candidateCount");
const bestScore = document.getElementById("bestScore");
const portfolioSignal = document.getElementById("portfolioSignal");
const themeText = document.getElementById("themeText");
const candidateGrid = document.getElementById("candidateGrid");
const selectionNotes = document.getElementById("selectionNotes");
const candidateTableBody = document.getElementById("candidateTableBody");

function setStatus(text, mode) {
  runStatus.textContent = text;
  runStatus.className = `status-badge ${mode}`;
}

function metricLine(label, value, scale = 220) {
  const width = Math.max(6, Math.min(100, (value / scale) * 100));
  return `
    <div class="mini">${label}: ${value}</div>
    <div class="bar"><span style="width:${width}%"></span></div>
  `;
}

function candidateCard(item, rank) {
  return `
    <article class="candidate-card">
      <div class="mini">Rank ${rank}</div>
      <div class="score">${item.weighted_score}</div>
      <div class="arch-label">PCIe Gen${item.pcie_generation} | ${item.channels} channels | ${item.nand_type}</div>
      <div class="mini">${item.controller_nodes_nm}nm controller | ${item.dram_cache_gb}GB DRAM | ${item.overprovisioning_pct}% OP</div>
      ${metricLine("Performance", item.metrics.performance)}
      ${metricLine("Endurance", item.metrics.endurance)}
      ${metricLine("Cost Efficiency", item.metrics.cost_efficiency)}
      ${metricLine("Power Efficiency", item.metrics.power_efficiency)}
      ${metricLine("Differentiation", item.metrics.differentiation, 80)}
    </article>
  `;
}

function noteCard(title, value, detail) {
  return `
    <article class="note-card">
      <div class="mini">${title}</div>
      <div class="arch-label">${value}</div>
      <div class="mini">${detail}</div>
    </article>
  `;
}

function buildNotes(candidates) {
  const leader = candidates[0];
  const mostEfficient = candidates.reduce((best, item) =>
    item.metrics.cost_efficiency > best.metrics.cost_efficiency ? item : best,
  candidates[0]);
  const strongestDifferentiation = candidates.reduce((best, item) =>
    item.metrics.differentiation > best.metrics.differentiation ? item : best,
  candidates[0]);

  selectionNotes.innerHTML = [
    noteCard("Primary Recommendation", `Gen${leader.pcie_generation} / ${leader.nand_type}`, "Best weighted fit for the current business priorities"),
    noteCard("Cost Leader", `${mostEfficient.metrics.cost_efficiency} cost score`, `${mostEfficient.channels} channels with ${mostEfficient.overprovisioning_pct}% OP`),
    noteCard("Differentiation Leader", `${strongestDifferentiation.metrics.differentiation} differentiation`, "Strongest option for roadmap storytelling and market separation"),
  ].join("");
}

function buildTable(candidates) {
  candidateTableBody.innerHTML = candidates
    .map(
      (item, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>Gen${item.pcie_generation} | ${item.channels}ch | ${item.nand_type} | ${item.dram_cache_gb}GB</td>
          <td>${item.weighted_score}</td>
          <td>${item.metrics.performance}</td>
          <td>${item.metrics.endurance}</td>
          <td>${item.metrics.cost_efficiency}</td>
          <td>${item.metrics.power_efficiency}</td>
          <td>${item.metrics.differentiation}</td>
        </tr>
      `,
    )
    .join("");
}

async function runTradeoff() {
  setStatus("Running", "running");
  runButton.disabled = true;

  try {
    const response = await fetch("/api/run");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();

    candidateCount.textContent = data.candidate_count;
    bestScore.textContent = data.summary.best_score;
    portfolioSignal.textContent = data.summary.best_score >= 110 ? "Aggressive performance posture" : "Balanced roadmap posture";
    themeText.textContent = data.summary.recommended_theme;
    candidateGrid.innerHTML = data.top_candidates.map((item, index) => candidateCard(item, index + 1)).join("");
    buildNotes(data.top_candidates);
    buildTable(data.top_candidates);

    setStatus("Completed", "success");
  } catch (error) {
    setStatus(`Error: ${error.message}`, "error");
  } finally {
    runButton.disabled = false;
  }
}

runButton.addEventListener("click", runTradeoff);
runTradeoff();
