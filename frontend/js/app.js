const API = {
  patterns: '/api/patterns',
  example:  '/api/patterns/example',
};

const CATEGORY_LABEL = {
  creational: '생성 패턴 (Creational)',
  structural: '구조 패턴 (Structural)',
  behavioral: '행동 패턴 (Behavioral)',
};

const CATEGORY_BADGE_CLASS = {
  creational: 'badge-creational',
  structural: 'badge-structural',
  behavioral: 'badge-behavioral',
};

let allPatterns = {};
let selectedPattern = null;

// ── 초기화 ──────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  loadPatternList();

  document.getElementById('searchBtn').addEventListener('click', handleSearch);
  document.getElementById('searchInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSearch();
  });
  document.getElementById('searchInput').addEventListener('input', handleFilter);

  // 전체화면 버튼 리스너 (정적 DOM에 한 번만 등록)
  document.getElementById('btnFsCopy').addEventListener('click', copyFullscreenCode);
  document.getElementById('btnFsClose').addEventListener('click', closeFullscreen);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeFullscreen();
  });

  // 결과 영역의 복사/전체화면 버튼 — 이벤트 위임
  document.getElementById('resultView').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    if (btn.classList.contains('btn-copy'))       copyCode(btn);
    if (btn.classList.contains('btn-fullscreen')) openFullscreen();
  });
});

// ── 패턴 목록 로드 ───────────────────────────────────────
async function loadPatternList() {
  try {
    const res  = await fetch(API.patterns);
    const data = await res.json();
    allPatterns = data.patterns;
    renderPatternList(allPatterns);
  } catch (err) {
    console.error('패턴 목록 로드 실패:', err);
  }
}

function renderPatternList(patterns) {
  const container = document.getElementById('patternList');
  container.innerHTML = '';

  for (const [cat, items] of Object.entries(patterns)) {
    const group = document.createElement('div');
    group.className = 'category-group';
    group.dataset.category = cat;

    const header = document.createElement('div');
    header.className = 'category-header';
    header.innerHTML = `
      <span class="category-label">
        <span class="cat-dot ${cat}"></span>
        ${CATEGORY_LABEL[cat]}
      </span>
      <span class="category-count">${items.length}</span>
    `;
    group.appendChild(header);

    items.forEach((p) => {
      const item = document.createElement('div');
      item.className = 'pattern-item';
      item.dataset.name = p.name;
      item.innerHTML = `
        <span class="pattern-name-en">${p.name}</span>
        <span class="pattern-name-ko">${p.name_ko}</span>
        ${p.available ? '<span class="cached-dot" title="예제 탑재됨"></span>' : ''}
      `;
      item.addEventListener('click', () => selectPattern(p.name));
      group.appendChild(item);
    });

    container.appendChild(group);
  }
}

// ── 검색 ─────────────────────────────────────────────────
function handleSearch() {
  const query = document.getElementById('searchInput').value.trim();
  if (!query) return;

  const matched = findPatternByName(query);
  if (matched) {
    selectPattern(matched);
    clearFilter();
  } else {
    handleFilter();
  }
}

function findPatternByName(query) {
  const q = query.toLowerCase();
  for (const items of Object.values(allPatterns)) {
    for (const p of items) {
      if (p.name.toLowerCase() === q || p.name_ko === query || p.name.toLowerCase().includes(q)) {
        return p.name;
      }
    }
  }
  return null;
}

// ── 실시간 필터링 ────────────────────────────────────────
function handleFilter() {
  const query = document.getElementById('searchInput').value.trim().toLowerCase();
  document.querySelectorAll('.pattern-item').forEach((item) => {
    item.classList.toggle('hidden', query.length > 0 && !item.dataset.name.toLowerCase().includes(query));
  });
  document.querySelectorAll('.category-group').forEach((group) => {
    const visible = group.querySelectorAll('.pattern-item:not(.hidden)');
    group.style.display = visible.length === 0 ? 'none' : '';
  });
}

function clearFilter() {
  document.getElementById('searchInput').value = '';
  document.querySelectorAll('.pattern-item').forEach((i) => i.classList.remove('hidden'));
  document.querySelectorAll('.category-group').forEach((g) => (g.style.display = ''));
}

// ── 패턴 선택 및 예제 로드 ──────────────────────────────
async function selectPattern(patternName) {
  selectedPattern = patternName;

  document.querySelectorAll('.pattern-item').forEach((item) => {
    item.classList.toggle('active', item.dataset.name === patternName);
  });

  showView('loading');

  try {
    const res = await fetch(API.example, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pattern_name: patternName }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || '알 수 없는 오류');
    }

    const data = await res.json();
    renderResult(data);
    showView('result');
  } catch (err) {
    showView('welcome');
    alert(`오류: ${err.message}`);
  }
}

// ── 결과 렌더링 ─────────────────────────────────────────
function renderResult(data) {
  const catClass = CATEGORY_BADGE_CLASS[data.category] || '';
  const catLabel = { creational: 'Creational', structural: 'Structural', behavioral: 'Behavioral' }[data.category] || data.category;

  const layersHtml = Array.isArray(data.layers_used) && data.layers_used.length
    ? `<div class="layers-wrap">
        <span class="layers-label">사용 레이어:</span>
        ${data.layers_used.map((l) => `<span class="layer-tag ${l.toLowerCase()}">${l}</span>`).join('')}
       </div>`
    : '';

  const benefitsHtml = Array.isArray(data.key_benefits)
    ? data.key_benefits.map((b) => `<li><span class="benefit-icon">✓</span><span>${b}</span></li>`).join('')
    : '';

  const flowHtml = Array.isArray(data.flow_description) && data.flow_description.length
    ? data.flow_description.map((step) => `<li class="flow-step">${escHtml(step)}</li>`).join('')
    : '';

  const html = `
    <div class="result-header">
      <div class="result-title-group">
        <h1 class="result-title">${escHtml(data.pattern_name)}</h1>
        <div class="result-badges">
          <span class="badge ${catClass}">${catLabel}</span>
          <span class="badge badge-cached">📦 사전 탑재</span>
        </div>
      </div>
    </div>

    <div class="result-section">
      <div class="section-header">
        <span class="section-num">01</span>
        <span class="section-title">패턴 개요</span>
      </div>
      <div class="section-body"><p>${escHtml(data.overview)}</p></div>
    </div>

    <div class="result-section">
      <div class="section-header">
        <span class="section-num">02</span>
        <span class="section-title">Spring Boot 활용 시나리오</span>
      </div>
      <div class="section-body"><p>${escHtml(data.use_case)}</p></div>
    </div>

    <div class="result-section">
      <div class="section-header">
        <span class="section-num">03</span>
        <span class="section-title">패키지 구조</span>
      </div>
      <div class="section-body">
        <pre class="package-tree">${escHtml(data.package_structure)}</pre>
      </div>
    </div>

    <div class="result-section">
      <div class="section-header">
        <span class="section-num">04</span>
        <span class="section-title">핵심 이점</span>
      </div>
      <div class="section-body">
        <ul class="benefits-list">${benefitsHtml}</ul>
      </div>
    </div>

    ${flowHtml ? `
    <div class="result-section">
      <div class="section-header">
        <span class="section-num">05</span>
        <span class="section-title">코드 흐름</span>
      </div>
      <div class="section-body">
        <ol class="flow-list">${flowHtml}</ol>
      </div>
    </div>` : ''}

    <div class="result-section">
      <div class="section-header">
        <span class="section-num">${flowHtml ? '06' : '05'}</span>
        <span class="section-title">예제 코드</span>
        ${layersHtml ? `<div class="section-header-layers">${layersHtml}</div>` : ''}
      </div>
      <div class="section-body" style="padding:0">
        <div class="code-container">
          <div class="code-toolbar">
            <span class="code-lang-badge">Java · Spring Boot</span>
            <div class="code-toolbar-actions">
              <button class="btn-copy">복사</button>
              <button class="btn-fullscreen">전체화면 ↗</button>
            </div>
          </div>
          <pre><code class="language-java" id="codeBlock">${escHtml(data.example_code)}</code></pre>
        </div>
      </div>
    </div>
  `;

  // 전체화면용 데이터 저장
  window._currentCode        = data.example_code;
  window._currentPatternName = data.pattern_name;

  const resultView = document.getElementById('resultView');
  resultView.innerHTML = html;
  resultView.scrollTop = 0;

  const codeBlock = document.getElementById('codeBlock');
  if (codeBlock) hljs.highlightElement(codeBlock);
}

// ── 코드 복사 (결과 화면) ───────────────────────────────
function copyCode(btn) {
  const code = document.getElementById('codeBlock')?.textContent || '';
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = '복사됨 ✓';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '복사'; btn.classList.remove('copied'); }, 2000);
  });
}

// ── 전체화면 열기 ────────────────────────────────────────
function openFullscreen() {
  const overlay    = document.getElementById('codeFullscreenOverlay');
  const fsCode     = document.getElementById('fsCodeBlock');
  const fsName     = document.getElementById('fsPatternName');

  if (!overlay || !fsCode) return;

  // 이미 하이라이팅 된 경우 초기화 후 재적용
  fsCode.removeAttribute('data-highlighted');
  fsCode.className = 'language-java';
  fsCode.textContent = window._currentCode || '';
  fsName.textContent  = window._currentPatternName || '';

  overlay.style.display = 'flex';
  document.body.style.overflow = 'hidden';

  hljs.highlightElement(fsCode);
}

// ── 전체화면 닫기 ────────────────────────────────────────
function closeFullscreen() {
  const overlay = document.getElementById('codeFullscreenOverlay');
  if (!overlay || overlay.style.display === 'none') return;
  overlay.style.display = 'none';
  document.body.style.overflow = '';
}

// ── 전체화면 코드 복사 ───────────────────────────────────
function copyFullscreenCode() {
  const btn  = document.getElementById('btnFsCopy');
  const code = document.getElementById('fsCodeBlock')?.textContent || '';
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = '복사됨 ✓';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '복사'; btn.classList.remove('copied'); }, 2000);
  });
}

// ── View 전환 ────────────────────────────────────────────
function showView(name) {
  document.getElementById('welcomeView').style.display = name === 'welcome' ? '' : 'none';
  document.getElementById('loadingView').style.display = name === 'loading' ? '' : 'none';
  document.getElementById('resultView').style.display  = name === 'result'  ? '' : 'none';
}

// ── Util ─────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
