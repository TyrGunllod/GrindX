(function () {
  'use strict';

  const API_BASE = window.grindx?.api?.base || '/api/v1';
  const CRONOGRAMA_URL = API_BASE + '/cronograma/tarefas';

  const CORES_STATUS = {
    todo: '#94a3b8',
    'in-progress': '#3b82f6',
    done: '#22c55e',
  };

  const STATUS_LABELS = {
    todo: 'A Fazer',
    'in-progress': 'Em Progresso',
    done: 'Concluída',
  };

  const ZOOM_LEVELS = [
    { key: 'Dia', cellWidth: 40, label: 'Dia' },
    { key: 'Semana', cellWidth: 20, label: 'Semana' },
    { key: 'Mês', cellWidth: 10, label: 'Mês' },
  ];

  const MESES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
  ];

  let tarefas = [];
  let projetos = [];
  let recursos = [];
  let zoomIndex = 1;
  let editingTaskId = null;
  let startDate = null;
  let endDate = null;
  let totalDays = 0;

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: 'Erro desconhecido' }));
      throw new Error(err.detail || err.message || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async function carregarTarefasGantt() {
    const projetoId = $('#filtro-projeto').value;
    const params = new URLSearchParams({ page: '1', page_size: '200' });
    if (projetoId) params.set('projeto_id', projetoId);
    try {
      const data = await apiFetch(`${CRONOGRAMA_URL}?${params}`);
      tarefas = data.items || [];
      renderizarGantt();
    } catch (e) {
      console.error('Erro ao carregar tarefas:', e);
    }
  }

  async function carregarProjetos() {
    try {
      const data = await apiFetch(`${API_BASE}/projetos?page=1&page_size=100`);
      projetos = data.items || [];
      renderizarFiltroProjetos();
      renderizarSelectProjetos();
    } catch (e) {
      console.error('Erro ao carregar projetos:', e);
    }
  }

  async function carregarRecursos() {
    try {
      const data = await apiFetch(`${API_BASE}/recursos?page=1&page_size=100`);
      recursos = data.items || [];
      renderizarSelectRecursos();
    } catch (e) {
      console.error('Erro ao carregar recursos:', e);
    }
  }

  function calcularDataRange() {
    if (tarefas.length === 0) {
      const hoje = new Date();
      startDate = new Date(hoje);
      startDate.setDate(hoje.getDate() - 7);
      endDate = new Date(hoje);
      endDate.setDate(hoje.getDate() + 30);
    } else {
      let min = null;
      let max = null;
      tarefas.forEach((t) => {
        const d1 = new Date(t.data_inicio + 'T12:00:00');
        const d2 = new Date(t.data_fim + 'T12:00:00');
        if (!min || d1 < min) min = new Date(d1);
        if (!max || d2 > max) max = new Date(d2);
      });
      startDate = new Date(min);
      startDate.setDate(startDate.getDate() - 7);
      endDate = new Date(max);
      endDate.setDate(endDate.getDate() + 14);
    }
    totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
  }

  function getCellWidth() {
    return ZOOM_LEVELS[zoomIndex].cellWidth;
  }

  function diasDesdeInicio(dataStr) {
    const d = new Date(dataStr + 'T12:00:00');
    return Math.floor((d - startDate) / (1000 * 60 * 60 * 24));
  }

  function calcularPosicao(tarefa) {
    const left = diasDesdeInicio(tarefa.data_inicio) * getCellWidth();
    const duracao = Math.max(
      1,
      Math.ceil(
        (new Date(tarefa.data_fim + 'T12:00:00') - new Date(tarefa.data_inicio + 'T12:00:00')) /
          (1000 * 60 * 60 * 24)
      ) + 1
    );
    const width = duracao * getCellWidth() - 4;
    return { left, width };
  }

  function renderizarGantt() {
    calcularDataRange();
    renderizarCabecalhoMeses();
    renderizarCabecalhoDias();
    renderizarBarras();
    renderizarLinhaHoje();
    renderizarLegenda();

    const scrollEl = $('#gantt-scroll');
    const totalWidth = totalDays * getCellWidth();
    $('#gantt-timeline').style.width = totalWidth + 'px';

    setTimeout(() => {
      const hojeLeft = diasDesdeInicio(new Date().toISOString().split('T')[0]) * getCellWidth();
      scrollEl.scrollLeft = hojeLeft - scrollEl.clientWidth / 3;
    }, 50);
  }

  function renderizarCabecalhoMeses() {
    const container = $('#gantt-header-months');
    container.innerHTML = '';
    let current = new Date(startDate);
    while (current < endDate) {
      const monthStart = new Date(current.getFullYear(), current.getMonth(), 1);
      const monthEnd = new Date(current.getFullYear(), current.getMonth() + 1, 0);
      const visStart = current > monthStart ? current : monthStart;
      const visEnd = endDate < monthEnd ? endDate : monthEnd;
      const days = Math.ceil((visEnd - visStart) / (1000 * 60 * 60 * 24)) + 1;
      const cell = document.createElement('div');
      cell.className = 'gantt-header-months__cell';
      cell.style.width = days * getCellWidth() + 'px';
      cell.textContent = MESES[current.getMonth()];
      container.appendChild(cell);
      current.setMonth(current.getMonth() + 1);
      current.setDate(1);
    }
  }

  function renderizarCabecalhoDias() {
    const container = $('#gantt-header-days');
    container.innerHTML = '';
    for (let i = 0; i < totalDays; i++) {
      const d = new Date(startDate);
      d.setDate(d.getDate() + i);
      const cell = document.createElement('div');
      cell.className = 'gantt-header-days__cell';
      if (d.getDay() === 0 || d.getDay() === 6) {
        cell.classList.add('gantt-header-days__cell--weekend');
      }
      cell.style.width = getCellWidth() + 'px';
      cell.textContent = d.getDate();
      container.appendChild(cell);
    }
  }

  function renderizarBarras() {
    const sidebar = $('#gantt-sidebar');
    const body = $('#gantt-body');
    sidebar.innerHTML = '<div class="gantt-sidebar__header">Tarefa</div>';
    body.innerHTML = '';
    body.style.width = totalDays * getCellWidth() + 'px';
    body.style.height = tarefas.length * 36 + 'px';

    tarefas.forEach((t) => {
      const pos = calcularPosicao(t);
      const projeto = projetos.find((p) => p.id === t.projeto_id);
      const dotColor = t.project_color || (projeto ? projeto.cor : '#94a3b8');
      const recurso = recursos.find((r) => r.id === t.responsavel_id);
      const assigneeColor = t.assignee_color || (recurso ? recurso.cor : '#6b7280');
      const assigneeName = t.assignee_name || (recurso ? (recurso.nome || '') : '');
      const initials = assigneeName ? assigneeName.charAt(0).toUpperCase() : '';

      const row = document.createElement('div');
      row.className = 'gantt-sidebar__row';
      row.dataset.id = t.id;
      row.innerHTML = `
        <span class="gantt-sidebar__dot" style="background:${dotColor}"></span>
        ${assigneeName ? `<span class="gantt-sidebar__avatar" style="background:${assigneeColor}">${initials}</span>` : ''}
        <span class="gantt-sidebar__title">${escapeHtml(t.titulo)}</span>
      `;
      sidebar.appendChild(row);

      const barRow = document.createElement('div');
      barRow.className = 'gantt-body__row';
      barRow.style.width = totalDays * getCellWidth() + 'px';

      const bar = document.createElement('div');
      bar.className = 'gantt-bar';
      bar.dataset.id = t.id;
      bar.style.left = pos.left + 'px';
      bar.style.width = Math.max(pos.width, 4) + 'px';
      bar.style.background = CORES_STATUS[t.status] || '#94a3b8';

      if (t.progresso > 0) {
        const progress = document.createElement('div');
        progress.className = 'gantt-bar__progress';
        progress.style.width = t.progresso + '%';
        bar.appendChild(progress);
      }

      bar.addEventListener('mouseenter', (e) => showTooltip(e, t));
      bar.addEventListener('mouseleave', hideTooltip);
      bar.addEventListener('click', () => abrirModalEdicao(t));

      barRow.appendChild(bar);
      body.appendChild(barRow);
    });
  }

  function renderizarLinhaHoje() {
    const hoje = new Date().toISOString().split('T')[0];
    const dias = diasDesdeInicio(hoje);
    if (dias < 0 || dias >= totalDays) return;

    const existing = document.querySelector('.gantt-today');
    if (existing) existing.remove();

    const line = document.createElement('div');
    line.className = 'gantt-today';
    line.style.left = dias * getCellWidth() + 'px';
    line.style.height = Math.max(tarefas.length * 36, 44) + 'px';

    const badge = document.createElement('div');
    badge.className = 'gantt-today__badge';
    badge.textContent = 'Hoje';
    line.appendChild(badge);

    $('#gantt-timeline').appendChild(line);
  }

  function renderizarLegenda() {
    const container = $('#gantt-legend');
    container.innerHTML = Object.entries(CORES_STATUS)
      .map(
        ([status, cor]) => `
        <div class="gantt-legend__item">
          <span class="gantt-legend__swatch" style="background:${cor}"></span>
          ${STATUS_LABELS[status]}
        </div>
      `
      )
      .join('') + `
      <div class="gantt-legend__item">
        <span class="gantt-legend__swatch" style="background:var(--danger,#ef4444)"></span>
        Hoje
      </div>
    `;
  }

  let tooltipEl = null;

  function showTooltip(e, t) {
    if (tooltipEl) tooltipEl.remove();
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'gantt-tooltip';
    const projetoNome = t.project_name || '—';
    const dataInicio = formatDate(t.data_inicio);
    const dataFim = formatDate(t.data_fim);
    tooltipEl.innerHTML = `
      <div class="gantt-tooltip__title">${escapeHtml(t.titulo)}</div>
      <div class="gantt-tooltip__row">
        <span class="gantt-tooltip__label">Projeto:</span>
        <span>${escapeHtml(projetoNome)}</span>
      </div>
      <div class="gantt-tooltip__row">
        <span class="gantt-tooltip__label">Datas:</span>
        <span>${dataInicio} — ${dataFim}</span>
      </div>
      <div class="gantt-tooltip__row">
        <span class="gantt-tooltip__label">Progresso:</span>
        <span>${t.progresso}%</span>
      </div>
    `;
    document.body.appendChild(tooltipEl);
    const rect = e.target.getBoundingClientRect();
    tooltipEl.style.left = rect.left + 'px';
    tooltipEl.style.top = rect.top - tooltipEl.offsetHeight - 8 + 'px';
  }

  function hideTooltip() {
    if (tooltipEl) {
      tooltipEl.remove();
      tooltipEl = null;
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr + 'T12:00:00');
    return d.toLocaleDateString('pt-BR');
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function todayStr() {
    return new Date().toISOString().split('T')[0];
  }

  function futureStr(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().split('T')[0];
  }

  function renderizarFiltroProjetos() {
    const sel = $('#filtro-projeto');
    const current = sel.value;
    sel.innerHTML = '<option value="">Todos os projetos</option>';
    projetos.forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.nome || `Projeto ${p.id}`;
      sel.appendChild(opt);
    });
    if (current) sel.value = current;
  }

  function renderizarSelectProjetos() {
    const sel = $('#tarefa-projeto-id');
    if (!sel) return;
    const current = sel.value;
    sel.innerHTML = '<option value="">Sem projeto</option>';
    projetos.forEach((p) => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.nome || `Projeto ${p.id}`;
      sel.appendChild(opt);
    });
    if (current) sel.value = current;
  }

  function renderizarSelectRecursos() {
    const sel = $('#tarefa-responsavel-id');
    if (!sel) return;
    const current = sel.value;
    sel.innerHTML = '<option value="">Sem responsável</option>';
    recursos.forEach((r) => {
      const opt = document.createElement('option');
      opt.value = r.id;
      opt.textContent = r.nome || `Recurso ${r.id}`;
      sel.appendChild(opt);
    });
    if (current) sel.value = current;
  }

  function abrirModalEdicao(tarefa) {
    editingTaskId = tarefa.id;
    $('#modal-title').textContent = 'Editar Tarefa';
    $('#tarefa-titulo').value = tarefa.titulo || '';
    if ($('#tarefa-descricao')) $('#tarefa-descricao').value = tarefa.descricao || '';
    $('#tarefa-status').value = tarefa.status || 'todo';
    $('#tarefa-prioridade').value = tarefa.prioridade || 'medium';
    $('#tarefa-data-inicio').value = tarefa.data_inicio || todayStr();
    $('#tarefa-data-fim').value = tarefa.data_fim || futureStr(7);
    $('#tarefa-progresso').value = tarefa.progresso || 0;
    const progLabel = $('#progresso-label');
    if (progLabel) progLabel.textContent = (tarefa.progresso || 0) + '%';
    $('#tarefa-projeto-id').value = tarefa.projeto_id || '';
    $('#tarefa-responsavel-id').value = tarefa.responsavel_id || '';
    $('#tarefa-modal').showModal();
  }

  function abrirModalNova() {
    editingTaskId = null;
    $('#modal-title').textContent = 'Nova Tarefa';
    $('#tarefa-titulo').value = '';
    if ($('#tarefa-descricao')) $('#tarefa-descricao').value = '';
    $('#tarefa-status').value = 'todo';
    $('#tarefa-prioridade').value = 'medium';
    $('#tarefa-data-inicio').value = todayStr();
    $('#tarefa-data-fim').value = futureStr(7);
    $('#tarefa-progresso').value = 0;
    const progLabel = $('#progresso-label');
    if (progLabel) progLabel.textContent = '0%';
    $('#tarefa-projeto-id').value = '';
    $('#tarefa-responsavel-id').value = '';
    $('#tarefa-modal').showModal();
  }

  function fecharModal() {
    $('#tarefa-modal').close();
    editingTaskId = null;
  }

  async function salvarTarefa(e) {
    e.preventDefault();
    const dados = {
      titulo: $('#tarefa-titulo').value.trim(),
      descricao: $('#tarefa-descricao') ? $('#tarefa-descricao').value.trim() || null : null,
      status: $('#tarefa-status').value,
      prioridade: $('#tarefa-prioridade').value,
      data_inicio: $('#tarefa-data-inicio').value,
      data_fim: $('#tarefa-data-fim').value,
      progresso: parseInt($('#tarefa-progresso').value) || 0,
      projeto_id: $('#tarefa-projeto-id').value ? parseInt($('#tarefa-projeto-id').value) : null,
      responsavel_id: $('#tarefa-responsavel-id').value ? parseInt($('#tarefa-responsavel-id').value) : null,
    };

    try {
      const url = `${API_BASE}/tarefas`;
      if (editingTaskId) {
        await apiFetch(`${url}/${editingTaskId}`, { method: 'PUT', body: JSON.stringify(dados) });
      } else {
        await apiFetch(url, { method: 'POST', body: JSON.stringify(dados) });
      }
      fecharModal();
      await carregarTarefasGantt();
    } catch (e) {
      alert('Erro ao salvar tarefa: ' + e.message);
    }
  }

  function zoomIn() {
    if (zoomIndex < ZOOM_LEVELS.length - 1) zoomIndex++;
    $('#zoom-label').textContent = ZOOM_LEVELS[zoomIndex].label;
    renderizarGantt();
  }

  function zoomOut() {
    if (zoomIndex > 0) zoomIndex--;
    $('#zoom-label').textContent = ZOOM_LEVELS[zoomIndex].label;
    renderizarGantt();
  }

  const modalContent = `{% include 'partials/tarefa-modal.html' %}`;
  if (modalContent) {
    $('#modal-body').innerHTML = modalContent;
  }

  async function init() {
    await Promise.all([carregarProjetos(), carregarRecursos()]);
    await carregarTarefasGantt();
  }

  document.addEventListener('DOMContentLoaded', () => {
    init();

    $('#btn-nova-tarefa').addEventListener('click', abrirModalNova);
    $('#zoom-in').addEventListener('click', zoomIn);
    $('#zoom-out').addEventListener('click', zoomOut);
    $('#filtro-projeto').addEventListener('change', carregarTarefasGantt);
    $('#modal-close').addEventListener('click', fecharModal);
    $('#modal-cancel').addEventListener('click', fecharModal);
    $('#tarefa-modal').addEventListener('close', fecharModal);
    $('#tarefa-modal').addEventListener('submit', salvarTarefa);
    $('#tarefa-progresso').addEventListener('input', (e) => {
      const label = $('#progresso-label');
      if (label) label.textContent = e.target.value + '%';
    });
  });
})();
