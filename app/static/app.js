const samples = {
  high: "Act now. This is your last chance to see the truth before it disappears. Everyone knows they are lying, and if you do not share this immediately, more people will be fooled. There is no middle ground, and the answer is obvious.",
  neutral:
    "A new policy brief reviewed three implementation options for transit funding. According to the report, ridership increased by 14 percent in pilot cities, but the authors note cost tradeoffs, timeline risks, and the need for further evaluation before statewide rollout.",
  mixed:
    "This proposal could make a real difference if adopted carefully. Supporters say it may improve access and reduce delays, but several assumptions still need evidence, and the long-term impact depends on funding, staffing, and how local agencies implement the plan.",
};

const metricLabels = {
  urgency_pressure: "Urgency Pressure",
  evidence_density: "Low Evidence Signal",
  arousal_intensity: "Arousal Intensity",
  counterargument_absence: "Counterargument Absence",
  claim_volume_vs_depth: "Claim Volume vs Depth",
  lexical_diversity: "Lexical Diversity",
  engagement_bait_score: "Engagement Bait Score",
};

const textInput = document.querySelector("#text-input");
const embeddingsToggle = document.querySelector("#embeddings-toggle");
const analyzeButton = document.querySelector("#analyze-button");
const errorMessage = document.querySelector("#error-message");
const resultsGrid = document.querySelector("#results-grid");
const rawJson = document.querySelector("#raw-json");
const metaSummary = document.querySelector("#meta-summary");

for (const button of document.querySelectorAll(".sample-button")) {
  button.addEventListener("click", () => {
    textInput.value = samples[button.dataset.sample];
    errorMessage.hidden = true;
  });
}

analyzeButton.addEventListener("click", async () => {
  errorMessage.hidden = true;
  analyzeButton.disabled = true;
  analyzeButton.textContent = "Analyzing...";

  try {
    const response = await fetch(`/analyze?embeddings=${embeddingsToggle.checked}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textInput.value }),
    });

    const data = await response.json();
    rawJson.textContent = JSON.stringify(data, null, 2);

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    renderResults(data);
  } catch (error) {
    resultsGrid.innerHTML = "";
    metaSummary.textContent = "Fix the request and try again.";
    errorMessage.textContent = error.message;
    errorMessage.hidden = false;
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analyze";
  }
});

function renderResults(data) {
  const cards = [];
  const metrics = [
    "urgency_pressure",
    "evidence_density",
    "arousal_intensity",
    "counterargument_absence",
    "claim_volume_vs_depth",
    "lexical_diversity",
  ];

  for (const key of metrics) {
    cards.push(metricCard(metricLabels[key], data[key].score, data[key].breakdown));
  }

  cards.push(scoreOnlyCard(metricLabels.engagement_bait_score, data.engagement_bait_score));
  resultsGrid.innerHTML = cards.join("");

  const meta = data.meta;
  metaSummary.textContent =
    `Embeddings requested: ${meta.embeddings_requested}. ` +
    `Embeddings used: ${meta.embeddings_used}. ` +
    `OpenAI available: ${meta.openai_available}. ` +
    `Vector backend: ${meta.vector_backend}.`;
}

function metricCard(title, score, breakdown) {
  const items = Object.entries(breakdown)
    .map(([key, value]) => `<li>${formatLabel(key)}: ${formatScore(value)}</li>`)
    .join("");
  const note =
    title === "Low Evidence Signal"
      ? '<p class="meta-summary">Higher means the text provides less supporting evidence.</p>'
      : "";

  return `
    <article class="result-card">
      <h3>${title}</h3>
      <div class="score-pill">${formatScore(score)}</div>
      ${note}
      <ul class="breakdown">${items}</ul>
    </article>
  `;
}

function scoreOnlyCard(title, score) {
  const value = score === null ? "Unavailable" : formatScore(score);
  return `
    <article class="result-card">
      <h3>${title}</h3>
      <div class="score-pill">${value}</div>
      <p class="meta-summary">Semantic similarity score from the optional embeddings layer.</p>
    </article>
  `;
}

function formatScore(value) {
  return Number(value).toFixed(2);
}

function formatLabel(value) {
  return value.replaceAll("_", " ");
}
