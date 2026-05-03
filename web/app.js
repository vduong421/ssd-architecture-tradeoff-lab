const runButton = document.getElementById("runButton");
const runStatus = document.getElementById("runStatus");
const aiBriefButton = document.getElementById("aiBriefButton");
const aiStatus = document.getElementById("aiStatus");
const aiBrief = document.getElementById("aiBrief");
const chatInput = document.getElementById("chatInput");
const chatButton = document.getElementById("chatButton");
const chatOutput = document.getElementById("chatOutput");
const chatStatus = document.getElementById("chatStatus");
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

if (typeof buildScoreChart === "function") {
  buildScoreChart(data.top_candidates);
}
setStatus("Completed", "success");
  } catch (error) {
    setStatus(`Error: ${error.message}`, "error");
  } finally {
    runButton.disabled = false;
  }
}

async function generateAiBrief() {
  aiStatus.textContent = "Analyzing...";
  aiBriefButton.disabled = true;
  aiBrief.textContent = "Building grounded SSD architecture analyst brief...";

  try {
    const response = await fetch("/api/ai-brief");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (data.mode === "local_llm") {
      aiStatus.textContent = `Local model: ${data.model}`;
      const result = data.ai_result || {};
      aiBrief.textContent = [
        `Brief: ${result.brief || ""}`,
        "",
        "Risk Flags:",
        ...((result.risk_flags || []).map((item) => `- ${item}`)),
        "",
        "Next Steps:",
        ...((result.next_steps || []).map((item) => `- ${item}`)),
        "",
        "Resume Bullets:",
        ...((result.resume_bullets || []).map((item) => `- ${item}`)),
      ].join("\n");
      return;
    }

    aiStatus.textContent = data.local_model_status || "Deterministic fallback";
    aiBrief.textContent = [
      `Brief: ${data.brief}`,
      "",
      "Risk Flags:",
      ...(data.risk_flags || []).map((item) => `- ${item}`),
      "",
      "Next Steps:",
      ...(data.next_steps || []).map((item) => `- ${item}`),
      "",
      "Resume Bullets:",
      ...(data.resume_bullets || []).map((item) => `- ${item}`),
    ].join("\n");
  } catch (error) {
    aiStatus.textContent = "AI brief failed";
    aiBrief.textContent = `Could not generate AI brief: ${error}`;
  } finally {
    aiBriefButton.disabled = false;
  }
}

async function askLocalAi() {
  const question = chatInput.value.trim();
  if (!question) {
    chatOutput.textContent = "Type a question first.";
    return;
  }

chatButton.disabled = true;
chatStatus.textContent = "Running Local AI...";
chatStatus.className = "status-badge running";
chatOutput.textContent = "Analyzing deterministic SSD scores and local AI context...";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
const evidence = Array.isArray(data.evidence)
  ? data.evidence.map(e => `- ${e}`).join("\n")
  : data.evidence || "";

const nextAction = Array.isArray(data.next_action)
  ? data.next_action.map(a => `- ${a}`).join("\n")
  : data.next_action || "";

function toList(items) {
  if (!items) return "";
  if (Array.isArray(items)) {
    return items.map(i => `<li>${i}</li>`).join("");
  }
  return `<li>${items}</li>`;
}

chatOutput.innerHTML = `
  <div><strong>Answer</strong>
    <ul>${toList(data.answer)}</ul>
  </div>

  <div><strong>Evidence</strong>
    <ul>${toList(data.evidence)}</ul>
  </div>

  <div><strong>Next Actions</strong>
    <ul>${toList(data.next_action)}</ul>
  </div>

  <div><strong>Recommendation</strong>
    <ul>${toList(data.recommendation)}</ul>
  </div>

  <div><strong>Decision</strong>
    <ul>${toList(data.decision)}</ul>
  </div>
`;
  } catch (error) {
    chatOutput.textContent = `Chat failed: ${error}`;
  } finally {
chatButton.disabled = false;
chatStatus.textContent = "Local AI Finished";
chatStatus.className = "status-badge success";
  }
}

function bindSampleButtons() {
  document.querySelectorAll(".qbtn").forEach((button) => {
    button.onclick = () => {
      const q = button.getAttribute("data-q") || "";
      chatInput.value = q;
      askLocalAi();
    };
  });
}

runButton.addEventListener("click", runTradeoff);
aiBriefButton.addEventListener("click", generateAiBrief);
chatButton.addEventListener("click", askLocalAi);

bindSampleButtons();
runTradeoff();
