(function () {
  'use strict';

  const API_BASE = window.grindx?.api?.base || '/api/v1';
  const TAREFAS_URL = API_BASE + '/tarefas';

  let tarefas = [];
  let projetos = [];
  let recursos = [];
  let editingTaskId = null;
  let currentTarefaId = null;

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // --- API ---
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

  async function carregarTarefas() {
    const projetoId = $('#filter-projeto').value;
    const status = $('#filter-status').value;
    const params = new URLSearchParams({ page: '1', page_size: '100' });
    if (projetoId) params.set('projeto_id', projetoId);
    if (status) params.set('status', status);
    try {
      const data = await apiFetch(`${TAREFAS_URL}?${params}`);
      tarefas = data.items || [];
      renderKanban();
    } catch (e) {
      console.error('Erro ao carregar tarefas:', e);
    }
  }

  async function carregarProjetos() {
    try {
      const data = await apiFetch(`${API_BASE}/projetos?page=1&page_size=100`);
      projetos = data.items || [];
      renderProjetoSelects();
    } catch (e) {
      console.error('Erro ao carregar projetos:', e);
    }
  }

  async function carregarRecursos() {
    try {
      const data = await apiFetch(`${API_BASE}/recursos?page=1&page_size=100`);
      recursos = data.items || [];
      renderRecursoSelects();
    } catch (e) {
      console.error('Erro ao carregar recursos:', e);
    }
  }

  function renderProjetoSelects() {
    const selects = $$('#filter-projeto, #field-projeto');
    selects.forEach((sel) => {
      const current = sel.value;
      sel.innerHTML = '';
      if (sel.id === 'filter-projeto') {
        sel.innerHTML = '<option value="">Todos os Projetos</option>';
      }
      projetos.forEach((p) => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.nome || p.titulo || `Projeto ${p.id}`;
        sel.appendChild(opt);
      });
      if (current) sel.value = current;
    });
  }

  function renderRecursoSelects() {
    const selects = $$('#field-responsavel, #drawer-responsavel');
    selects.forEach((sel) => {
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
    });
  }

  // --- Kanban ---
  function renderKanban() {
    const columns = { todo: [], 'in-progress': [], done: [] };
    tarefas.forEach((t) => {
      if (columns[t.status]) columns[t.status].push(t);
    });

    ['todo', 'in-progress', 'done'].forEach((status) => {
      const container = $(`#column-${status}`);
      if (!container) return;
      const items = columns[status];
      if (items.length === 0) {
        container.innerHTML = '<div class="empty-column">Nenhuma tarefa</div>';
        return;
      }
      container.innerHTML = items.map((t) => renderCard(t)).join('');
    });
  }

  function renderCard(t) {
    const prioridadeLabel = { low: 'Baixa', medium: 'Média', high: 'Alta' };
    const prioridadeClass = `priority-${t.prioridade}`;
    const assigneeName = getAssigneeName(t.responsavel_id);
    const assigneColor = stringToColor(assigneeName);
    const projetoNome = getProjetoNome(t.projeto_id);
    const projetoColor = stringToColor(projetoNome);

    return `
      <div class="task-card" data-id="${t.id}">
        <div class="task-card-header">
          <span class="task-card-title">${escapeHtml(t.titulo)}</span>
        </div>
        ${t.projeto_id ? `<div class="task-card-project"><span class="project-dot" style="background:${projetoColor}"></span>${escapeHtml(projetoNome)}</div>` : ''}
        ${t.descricao ? `<div class="task-card-desc">${escapeHtml(t.descricao)}</div>` : ''}
        <div class="task-card-progress">
          <div class="progress-bar"><div class="progress-fill" style="width:${t.progresso}%"></div></div>
          <div class="progress-text">${t.progresso}%</div>
        </div>
        <div class="task-card-meta">
          <span class="task-card-priority ${prioridadeClass}">${prioridadeLabel[t.prioridade] || t.prioridade}</span>
          <span class="task-card-date">${formatDate(t.data_fim)}</span>
          ${assigneeName ? `<div class="task-card-assignee" style="background:${assigneColor}">${assigneeName.charAt(0).toUpperCase()}</div>` : ''}
        </div>
        <div class="task-card-actions">
          <select class="status-select" data-action="status" data-id="${t.id}">
            <option value="todo" ${t.status === 'todo' ? 'selected' : ''}>A Fazer</option>
            <option value="in-progress" ${t.status === 'in-progress' ? 'selected' : ''}>Em Progresso</option>
            <option value="done" ${t.status === 'done' ? 'selected' : ''}>Concluída</option>
          </select>
          <button data-action="edit" data-id="${t.id}">Editar</button>
          <button data-action="registros" data-id="${t.id}">Registros</button>
          <button data-action="delete" data-id="${t.id}">Excluir</button>
        </div>
      </div>
    `;
  }

  function getAssigneeName(id) {
    if (!id) return '';
    const r = recursos.find((r) => r.id === id);
    return r ? (r.nome || `Recurso ${r.id}`) : '';
  }

  function getProjetoNome(id) {
    if (!id) return '';
    const p = projetos.find((p) => p.id === id);
    return p ? (p.nome || p.titulo || `Projeto ${p.id}`) : '';
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

  function stringToColor(str) {
    if (!str) return '#6b7280';
    let hash = 0;
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 55%, 50%)`;
  }

  // --- Modal Tarefa ---
  function openModal(tarefa = null) {
    editingTaskId = tarefa ? tarefa.id : null;
    $('#modal-title').textContent = tarefa ? 'Editar Tarefa' : 'Nova Tarefa';
    $('#field-titulo').value = tarefa ? tarefa.titulo : '';
    $('#field-descricao').value = tarefa ? (tarefa.descricao || '') : '';
    $('#field-projeto').value = tarefa ? (tarefa.projeto_id || '') : '';
    $('#field-responsavel').value = tarefa ? (tarefa.responsavel_id || '') : '';
    $('#field-data-inicio').value = tarefa ? tarefa.data_inicio : todayStr();
    $('#field-data-fim').value = tarefa ? tarefa.data_fim : futureStr(7);
    $('#field-status').value = tarefa ? tarefa.status : 'todo';
    $('#field-prioridade').value = tarefa ? tarefa.prioridade : 'medium';
    $('#field-progresso').value = tarefa ? tarefa.progresso : 0;
    $('#progresso-value').textContent = tarefa ? tarefa.progresso : 0;
    $('#modal-tarefa').style.display = 'flex';
  }

  function closeModal() {
    $('#modal-tarefa').style.display = 'none';
    editingTaskId = null;
  }

  function todayStr() {
    const d = new Date();
    return d.toISOString().split('T')[0];
  }

  function futureStr(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().split('T')[0];
  }

  // --- Drawer Registros ---
  let registros = [];

  async function openDrawerRegistros(tarefaId) {
    currentTarefaId = tarefaId;
    const t = tarefas.find((t) => t.id === tarefaId);
    $('#drawer-tarefa-info').textContent = t ? t.titulo : '';
    $('#drawer-registros').style.display = 'flex';
    await carregarRegistros();
  }

  function closeDrawer() {
    $('#drawer-registros').style.display = 'none';
    currentTarefaId = null;
    registros = [];
  }

  async function carregarRegistros() {
    if (!currentTarefaId) return;
    try {
      const data = await apiFetch(`${TAREFAS_URL}/${currentTarefaId}/registros?page=1&page_size=50`);
      registros = data.items || [];
      renderRegistros();
    } catch (e) {
      console.error('Erro ao carregar registros:', e);
    }
  }

  function renderRegistros() {
    const timeline = $('#registros-timeline');
    const empty = $('#registro-empty');
    if (registros.length === 0) {
      timeline.innerHTML = '';
      empty.classList.remove('hidden');
      return;
    }
    empty.classList.add('hidden');
    timeline.innerHTML = registros.map((r) => {
      const tipoLabel = r.tipo === 'decisao' ? 'Decisão' : 'Log';
      const autorNome = getAssigneeName(r.autor_id);
      return `
        <div class="registro-item">
          <div class="registro-item-header">
            <span class="registro-tipo-badge registro-tipo-${r.tipo}">${tipoLabel}</span>
            <span class="registro-data">${formatDateTime(r.criado_em)}</span>
            ${autorNome ? `<span class="registro-autor">${escapeHtml(autorNome)}</span>` : ''}
          </div>
          <div class="registro-conteudo">${escapeHtml(r.conteudo)}</div>
        </div>
      `;
    }).join('');
  }

  function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleString('pt-BR');
  }

  // --- Event Handlers ---
  $('#btn-nova-tarefa').addEventListener('click', () => openModal());

  $('#btn-modal-close').addEventListener('click', closeModal);
  $('#btn-cancelar').addEventListener('click', closeModal);

  $('#modal-tarefa').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });

  $('#field-progresso').addEventListener('input', (e) => {
    $('#progresso-value').textContent = e.target.value;
  });

  $('#form-tarefa').addEventListener('submit', async (e) => {
    e.preventDefault();
    const dados = {
      titulo: $('#field-titulo').value,
      descricao: $('#field-descricao').value || null,
      projeto_id: $('#field-projeto').value ? parseInt($('#field-projeto').value) : null,
      responsavel_id: $('#field-responsavel').value ? parseInt($('#field-responsavel').value) : null,
      data_inicio: $('#field-data-inicio').value,
      data_fim: $('#field-data-fim').value,
      status: $('#field-status').value,
      prioridade: $('#field-prioridade').value,
      progresso: parseInt($('#field-progresso').value),
    };

    try {
      if (editingTaskId) {
        await apiFetch(`${TAREFAS_URL}/${editingTaskId}`, {
          method: 'PUT',
          body: JSON.stringify(dados),
        });
      } else {
        await apiFetch(TAREFAS_URL, {
          method: 'POST',
          body: JSON.stringify(dados),
        });
      }
      closeModal();
      await carregarTarefas();
    } catch (e) {
      alert('Erro ao salvar tarefa: ' + e.message);
    }
  });

  // Delegated events on kanban
  $('#kanban-board').addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const action = btn.dataset.action;
    const id = parseInt(btn.dataset.id);

    if (action === 'edit') {
      const t = tarefas.find((t) => t.id === id);
      if (t) openModal(t);
    } else if (action === 'delete') {
      if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        try {
          await apiFetch(`${TAREFAS_URL}/${id}`, { method: 'DELETE' });
          await carregarTarefas();
        } catch (e) {
          alert('Erro ao excluir: ' + e.message);
        }
      }
    } else if (action === 'registros') {
      openDrawerRegistros(id);
    }
  });

  $('#kanban-board').addEventListener('change', async (e) => {
    const sel = e.target.closest('.status-select');
    if (!sel) return;
    const id = parseInt(sel.dataset.id);
    const newStatus = sel.value;
    const t = tarefas.find((t) => t.id === id);
    if (!t) return;

    const progress = newStatus === 'done' ? 100 : newStatus === 'todo' ? 0 : t.progresso;
    try {
      await apiFetch(`${TAREFAS_URL}/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ ...t, status: newStatus, progresso: progress }),
      });
      await carregarTarefas();
    } catch (e) {
      alert('Erro ao atualizar status: ' + e.message);
    }
  });

  // Filter events
  $('#filter-projeto').addEventListener('change', carregarTarefas);
  $('#filter-status').addEventListener('change', carregarTarefas);

  // Drawer events
  $('#btn-drawer-close').addEventListener('click', closeDrawer);
  $('#drawer-registros').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeDrawer();
  });

  $('#form-registro').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentTarefaId) return;
    const dados = {
      tipo: $('#field-registro-tipo').value,
      conteudo: $('#field-registro-conteudo').value,
    };
    try {
      await apiFetch(`${TAREFAS_URL}/${currentTarefaId}/registros`, {
        method: 'POST',
        body: JSON.stringify(dados),
      });
      $('#field-registro-conteudo').value = '';
      await carregarRegistros();
    } catch (e) {
      alert('Erro ao adicionar registro: ' + e.message);
    }
  });

  // --- Init ---
  async function init() {
    await Promise.all([carregarProjetos(), carregarRecursos()]);
    await carregarTarefas();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
