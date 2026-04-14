/* ── State ─────────────────────────────────────────────────────────────── */
let hwRows = [];
let lastResult = null;
let currentDocxFilename = null;
let currentStep = 1;

/* ── Step navigation ─────────────────────────────────────────────────────── */
function goStep(n) {
  if (n === 3) buildReviewCards();
  if (n === 4 && !lastResult) return;

  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', parseInt(el.dataset.step) === n);
  });
  document.getElementById(`step-${n}`).classList.add('active');
  currentStep = n;
  window.scrollTo(0, 0);
}

/* ── Competitor select ───────────────────────────────────────────────────── */
function onCompetitorChange() {
  const sel = document.getElementById('competitor-select');
  const opt = sel.selectedOptions[0];
  const isCustom = sel.value === '__custom__';

  document.getElementById('comp-url-group').style.display = isCustom ? 'none' : '';
  document.getElementById('custom-name-group').style.display = isCustom ? '' : 'none';
  document.getElementById('custom-url-group').style.display  = isCustom ? '' : 'none';

  if (!isCustom && opt && opt.dataset.url) {
    document.getElementById('competitor-url').value = opt.dataset.url;
  } else {
    document.getElementById('competitor-url').value = '';
  }
}

function onProviderChange() {
  const p = document.getElementById('provider-select').value;
  document.getElementById('api-key-label').innerHTML =
    p === 'anthropic'
      ? 'Anthropic API key <span class="optional">(or set ANTHROPIC_API_KEY env)</span>'
      : 'OpenAI API key <span class="optional">(or set OPENAI_API_KEY env)</span>';
  document.getElementById('api-key').placeholder = p === 'anthropic' ? 'sk-ant-…' : 'sk-…';
}

/* ── Hardware table ──────────────────────────────────────────────────────── */
function renderTable() {
  const body = document.getElementById('hw-body');
  body.innerHTML = hwRows.map((r, i) => `
    <tr>
      <td class="col-hw">
        <input value="${esc(r.name)}" oninput="hwRows[${i}].name=this.value;updateRowCount()"
               placeholder="Hardware name"/>
      </td>
      <td class="col-desc">
        <input value="${esc(r.description)}" oninput="hwRows[${i}].description=this.value"
               placeholder="Short description"/>
      </td>
      <td class="col-tit">
        <select onchange="hwRows[${i}].titanium=this.value">
          <option ${r.titanium === 'Yes' ? 'selected' : ''}>Yes</option>
          <option ${r.titanium === 'No'  ? 'selected' : ''}>No</option>
        </select>
      </td>
      <td class="col-del">
        <button class="btn sm danger" onclick="removeRow(${i})">✕</button>
      </td>
    </tr>`).join('');
  updateRowCount();
}

function updateRowCount() {
  const n = hwRows.filter(r => r.name.trim()).length;
  document.getElementById('row-count').textContent = `${n} row${n !== 1 ? 's' : ''}`;
}

function addRow(name = '', description = '', titanium = 'Yes') {
  hwRows.push({ name, description, titanium });
  renderTable();
}

function removeRow(i) {
  hwRows.splice(i, 1);
  renderTable();
}

function clearAll() {
  hwRows = [];
  renderTable();
}

async function loadDefaults() {
  try {
    const res = await fetch('/api/hardware/defaults');
    const data = await res.json();
    hwRows = data.map(d => ({ name: d.name, description: d.description, titanium: d.titanium }));
    renderTable();
  } catch (e) {
    alert('Failed to load defaults: ' + e.message);
  }
}

/* ── Review cards ─────────────────────────────────────────────────────────── */
function buildReviewCards() {
  const sel    = document.getElementById('competitor-select');
  const isCustom = sel.value === '__custom__';
  const compName = isCustom
    ? (document.getElementById('custom-name').value || '—')
    : (sel.selectedOptions[0]?.dataset.name || '—');
  const compUrl = isCustom
    ? (document.getElementById('custom-url').value || '—')
    : (document.getElementById('competitor-url').value || '—');
  const provider = document.getElementById('provider-select').value;
  const hw = hwRows.filter(r => r.name.trim()).length;

  document.getElementById('review-cards').innerHTML = `
    <div class="review-card">
      <div class="rc-label">Competitor</div>
      <div class="rc-value">${esc(compName)}</div>
      <div class="rc-sub">${esc(compUrl)}</div>
    </div>
    <div class="review-card">
      <div class="rc-label">LLM provider</div>
      <div class="rc-value">${provider === 'anthropic' ? 'Anthropic Claude' : 'OpenAI GPT-4o'}</div>
    </div>
    <div class="review-card">
      <div class="rc-label">Hardware rows</div>
      <div class="rc-value">${hw}</div>
      <div class="rc-sub">items to compare</div>
    </div>
    <div class="review-card">
      <div class="rc-label">Output format</div>
      <div class="rc-value">Word (.docx)</div>
      <div class="rc-sub">+ in-page table</div>
    </div>`;
}

/* ── Run analysis ─────────────────────────────────────────────────────────── */
async function runAnalysis() {
  const sel = document.getElementById('competitor-select');
  const isCustom = sel.value === '__custom__';
  const hw = hwRows.filter(r => r.name.trim());

  if (!sel.value && !isCustom) { alert('Please select a competitor first.'); return; }
  if (hw.length === 0) { alert('Add at least one hardware row before running.'); return; }

  const runBtn = document.getElementById('run-btn');
  const runLabel = document.getElementById('run-label');
  const status = document.getElementById('run-status');

  runBtn.disabled = true;
  runLabel.textContent = 'Running…';
  status.innerHTML = '<div class="spinner active"></div> Sending to AI — this may take 20–40 seconds…';


  // Just set api_key to empty string '' — the server will always use the key from the INI file.
  // ****************
  const payload = {
    competitor_slug:        isCustom ? '' : sel.value,
    custom_competitor_name: isCustom ? document.getElementById('custom-name').value : '',
    custom_competitor_url:  isCustom ? document.getElementById('custom-url').value  : '',
    provider: document.getElementById('provider-select').value,
    api_key:  '',
    hardware: hw,
};
//#################


  // const payload = {
  //   competitor_slug: isCustom ? '' : sel.value,
  //   custom_competitor_name: isCustom ? document.getElementById('custom-name').value : '',
  //   custom_competitor_url:  isCustom ? document.getElementById('custom-url').value  : '',
  //   provider: document.getElementById('provider-select').value,
  //   api_key:  document.getElementById('api-key').value,
  //   hardware: hw,
  // };


  try {
    const res  = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      status.innerHTML = `<span style="color:var(--red)">Error: ${esc(data.error || 'Unknown error')}</span>`;
      runBtn.disabled = false;
      runLabel.textContent = '▶ Retry analysis';
      return;
    }

    lastResult = data;
    currentDocxFilename = data.docx_filename;

    // Unlock results tab
    const navR = document.getElementById('nav-results');
    navR.style.opacity = '1';
    navR.style.pointerEvents = 'auto';

    renderResults(data);
    goStep(4);

  } catch (e) {
    status.innerHTML = `<span style="color:var(--red)">Network error: ${esc(e.message)}</span>`;
  } finally {
    runBtn.disabled = false;
    runLabel.textContent = '▶ Start analysis';
  }
}

/* ── Render results ──────────────────────────────────────────────────────── */
function renderResults(data) {
  // Summary sub
  document.getElementById('result-sub').textContent =
    `Titanium vs ${data.competitor} · ${data.generated_at}`;

  // Summary cards
  document.getElementById('summary-bar').innerHTML = `
    <div class="summary-card"><div class="sc-label">Total hardware</div><div class="sc-val total">${data.summary.total}</div></div>
    <div class="summary-card"><div class="sc-label">${data.competitor} — Yes</div><div class="sc-val yes">${data.summary.yes}</div></div>
    <div class="summary-card"><div class="sc-label">${data.competitor} — Partial</div><div class="sc-val partial">${data.summary.partial}</div></div>
    <div class="summary-card"><div class="sc-label">${data.competitor} — No</div><div class="sc-val no">${data.summary.no}</div></div>`;

  // Column header
  document.getElementById('comp-col-hdr').textContent = data.competitor;

  // Table rows
  const body = document.getElementById('result-body');
  body.innerHTML = data.rows.map((r, i) => {
    const titCls  = r.titanium === 'Yes' ? 'yes' : 'no';
    const compCls = r.competitor === 'Yes' ? 'yes' : r.competitor === 'Partial' ? 'partial' : 'no';
    return `<tr data-filter="${r.competitor}" data-idx="${i}">
      <td class="hw-name">${esc(r.hardware)}</td>
      <td class="hw-desc">${esc(r.description)}</td>
      <td class="hw-using">${esc(r.companies_using || 'None')}</td>
      <td><span class="pill ${titCls}">${r.titanium}</span></td>
      <td><span class="pill ${compCls}">${r.competitor}</span></td>
<!--      <td class="hw-notes">${esc(r.competitor_notes || '')}</td>-->
    </tr>`;
  }).join('');

  // Show download button
  const dlBtn = document.getElementById('download-btn');
  dlBtn.style.display = 'inline-flex';

  applyFilter('all');
}

/* ── Filter ──────────────────────────────────────────────────────────────── */
function applyFilter(val) {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === val);
  });
  document.querySelectorAll('#result-body tr').forEach(tr => {
    const show = val === 'all' || tr.dataset.filter === val;
    tr.classList.toggle('hidden-row', !show);
  });
}

/* ── Download ─────────────────────────────────────────────────────────────── */
function downloadReport() {
  if (currentDocxFilename) {
    window.location.href = `/download/${encodeURIComponent(currentDocxFilename)}`;
  }
}

/* ── Utility ─────────────────────────────────────────────────────────────── */
function esc(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ── Init ─────────────────────────────────────────────────────────────────── */

// add new functionality
// document.addEventListener('DOMContentLoaded', () => {
//   loadDefaults();
// });
document.addEventListener('DOMContentLoaded', () => {
  loadDefaults();
  loadConfig();
});

async function loadConfig() {
  try {
    const res  = await fetch('/api/config');
    const cfg  = await res.json();

    const keyInput   = document.getElementById('api-key');
    const keyLabel   = document.getElementById('api-key-label');
    const modelInfo  = document.getElementById('provider-select');

    if (cfg.api_key_set) {
      keyInput.value       = '**************';
      keyInput.readOnly    = true;
      keyInput.placeholder = '';

      keyInput.readOnly    = true;
      keyInput.title       = 'API key loaded from tis_gap_app.ini';
      keyInput.style.color = 'var(--gray-400)';
      keyLabel.innerHTML   = `API key <span class="optional">(loaded from ini — model: ${cfg.model})</span>`;
    } else {
      keyInput.readOnly    = false;
      keyInput.placeholder = 'sk-… (not found in ini)';
      keyLabel.innerHTML   = `API key <span class="optional" style="color:var(--red)">not found in tis_gap_app.ini — enter manually</span>`;
    }
  } catch(e) {
    console.warn('Could not load config:', e);
  }
}