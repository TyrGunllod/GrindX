let projetos = []
let gerentes = []
let editingId = null
let projetoToDelete = null
let selectedColor = '#3b82f6'

const CORES = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16',
]

const STATUS_LABELS = {
  planning: 'Planejamento',
  active: 'Ativo',
  completed: 'Concluido',
  'on-hold': 'Em Espera',
}

const STATUS_CLASSES = {
  planning: 'badge--blue',
  active: 'badge--green',
  completed: 'badge--gray',
  'on-hold': 'badge--yellow',
}

const api = {
  async listarProjetos() {
    const res = await fetch('/v1/projetos')
    if (!res.ok) throw new Error('Erro ao carregar projetos')
    const data = await res.json()
    return data.items || data
  },

  async criarProjeto(dados) {
    const res = await fetch('/v1/projetos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Erro ao criar projeto')
    }
    return res.json()
  },

  async atualizarProjeto(id, dados) {
    const res = await fetch(`/v1/projetos/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Erro ao atualizar projeto')
    }
    return res.json()
  },

  async excluirProjeto(id) {
    const res = await fetch(`/v1/projetos/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Erro ao excluir projeto')
    return res.json()
  },

  async listarGerentes() {
    try {
      const res = await fetch('/v1/usuarios')
      if (!res.ok) return []
      const data = await res.json()
      return data.items || data
    } catch {
      return []
    }
  },
}

function renderProjetos() {
  const grid = document.getElementById('projetos-grid')
  const empty = document.getElementById('empty-state')

  if (projetos.length === 0) {
    grid.innerHTML = ''
    empty.classList.remove('hidden')
    return
  }

  empty.classList.add('hidden')
  grid.innerHTML = projetos.map(renderCard).join('')
}

function renderCard(projeto) {
  const dataInicio = formatDate(projeto.data_inicio)
  const dataFim = formatDate(projeto.data_fim)
  const gerente = gerentes.find(g => g.id === projeto.gerente_id)
  const gerenteInicial = gerente ? gerente.nome.charAt(0).toUpperCase() : ''
  const gerenteNome = gerente ? gerente.nome.split(' ')[0] : ''
  const gerenteCor = gerente ? gerente.cor : '#888'

  return `
    <div class="projeto-card" data-id="${projeto.id}">
      <div class="projeto-card__color-bar" style="background-color: ${projeto.cor}"></div>
      <div class="projeto-card__header">
        <div class="projeto-card__title-group">
          <h3 class="projeto-card__title">${escapeHtml(projeto.nome)}</h3>
          <span class="badge ${STATUS_CLASSES[projeto.status] || ''}">${STATUS_LABELS[projeto.status] || projeto.status}</span>
        </div>
        <div class="projeto-card__menu">
          <button class="btn-icon" data-action="menu" onclick="toggleMenu(this)">...</button>
          <div class="dropdown-content hidden">
            <button data-action="editar">Editar</button>
            <button data-action="excluir" class="text-danger">Excluir</button>
          </div>
        </div>
      </div>
      <p class="projeto-card__descricao">${escapeHtml(projeto.descricao || '')}</p>
      <div class="projeto-card__datas">
        <span>${dataInicio} - ${dataFim}</span>
      </div>
      <div class="projeto-card__footer">
        <span class="projeto-card__task-count"></span>
        <div class="projeto-card__gerente">
          ${gerente ? `<div class="avatar" style="background-color: ${gerenteCor}">${gerenteInicial}</div><span>${escapeHtml(gerenteNome)}</span>` : ''}
        </div>
      </div>
    </div>
  `
}

function renderColorPalette() {
  const container = document.getElementById('color-palette')
  container.innerHTML = CORES.map(cor => `
    <button type="button" class="color-swatch ${selectedColor === cor ? 'color-swatch--selected' : ''}"
      style="background-color: ${cor}"
      data-cor="${cor}"
      onclick="selectCor('${cor}')">
    </button>
  `).join('')
}

function renderGerentesSelect() {
  const select = document.getElementById('input-gerente')
  select.innerHTML = '<option value="">Selecione</option>' +
    gerentes.map(g => `<option value="${g.id}">${escapeHtml(g.nome)}</option>`).join('')
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + (dateStr.includes('T') ? '' : 'T12:00:00'))
  return d.toLocaleDateString('pt-BR')
}

function escapeHtml(text) {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function selectCor(cor) {
  selectedColor = cor
  document.querySelectorAll('.color-swatch').forEach(el => {
    el.classList.toggle('color-swatch--selected', el.dataset.cor === cor)
  })
}

function toggleMenu(btn) {
  const dropdown = btn.nextElementSibling
  dropdown.classList.toggle('hidden')
  const close = (e) => {
    if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add('hidden')
      document.removeEventListener('click', close)
    }
  }
  setTimeout(() => document.addEventListener('click', close), 0)
}

function abrirModalCriacao() {
  editingId = null
  document.getElementById('modal-title').textContent = 'Novo Projeto'
  document.getElementById('btn-modal-salvar').textContent = 'Criar Projeto'
  document.getElementById('projeto-form').reset()
  const hoje = new Date().toISOString().split('T')[0]
  const futuro = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  document.getElementById('input-data-inicio').value = hoje
  document.getElementById('input-data-fim').value = futuro
  selectedColor = CORES[0]
  renderColorPalette()
  document.getElementById('input-status').value = 'planning'
  document.getElementById('input-gerente').value = ''
  document.getElementById('projeto-modal').classList.remove('hidden')
}

function abrirModalEdicao(projeto) {
  editingId = projeto.id
  document.getElementById('modal-title').textContent = 'Editar Projeto'
  document.getElementById('btn-modal-salvar').textContent = 'Salvar'
  document.getElementById('input-nome').value = projeto.nome
  document.getElementById('input-descricao').value = projeto.descricao || ''
  document.getElementById('input-data-inicio').value = projeto.data_inicio
  document.getElementById('input-data-fim').value = projeto.data_fim
  document.getElementById('input-status').value = projeto.status
  document.getElementById('input-gerente').value = projeto.gerente_id || ''
  selectedColor = projeto.cor
  renderColorPalette()
  document.getElementById('projeto-modal').classList.remove('hidden')
}

function fecharModal() {
  document.getElementById('projeto-modal').classList.add('hidden')
  editingId = null
}

async function handleSubmit(e) {
  e.preventDefault()
  const dados = {
    nome: document.getElementById('input-nome').value.trim(),
    descricao: document.getElementById('input-descricao').value.trim() || null,
    status: document.getElementById('input-status').value,
    data_inicio: document.getElementById('input-data-inicio').value,
    data_fim: document.getElementById('input-data-fim').value,
    cor: selectedColor,
    gerente_id: document.getElementById('input-gerente').value || null,
  }

  try {
    if (editingId) {
      const atualizado = await api.atualizarProjeto(editingId, dados)
      projetos = projetos.map(p => p.id === editingId ? atualizado : p)
    } else {
      const novo = await api.criarProjeto(dados)
      projetos.push(novo)
    }
    renderProjetos()
    fecharModal()
  } catch (err) {
    mostrarErro(err.message)
  }
}

async function confirmarExclusao() {
  try {
    await api.excluirProjeto(projetoToDelete)
    projetos = projetos.filter(p => p.id !== projetoToDelete)
    projetoToDelete = null
    renderProjetos()
  } catch (err) {
    mostrarErro(err.message)
  }
}

function mostrarErro(msg) {
  const toast = document.getElementById('toast')
  toast.textContent = msg
  toast.classList.remove('hidden')
  setTimeout(() => toast.classList.add('hidden'), 4000)
}

async function init() {
  const loading = document.getElementById('loading')
  loading.classList.remove('hidden')
  try {
    projetos = await api.listarProjetos()
    gerentes = await api.listarGerentes()
    renderProjetos()
    renderColorPalette()
    renderGerentesSelect()
  } catch (err) {
    mostrarErro(err.message)
  } finally {
    loading.classList.add('hidden')
  }
}

document.addEventListener('DOMContentLoaded', () => {
  init()

  document.getElementById('btn-novo-projeto').addEventListener('click', abrirModalCriacao)
  document.getElementById('btn-empty-criar').addEventListener('click', abrirModalCriacao)
  document.getElementById('projeto-form').addEventListener('submit', handleSubmit)
  document.getElementById('btn-modal-cancelar').addEventListener('click', fecharModal)

  document.getElementById('projeto-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) fecharModal()
  })

  document.getElementById('btn-confirm-cancelar').addEventListener('click', () => {
    document.getElementById('confirm-dialog').classList.add('hidden')
    projetoToDelete = null
  })

  document.getElementById('btn-confirm-excluir').addEventListener('click', () => {
    if (projetoToDelete) {
      confirmarExclusao()
      document.getElementById('confirm-dialog').classList.add('hidden')
    }
  })

  document.getElementById('confirm-dialog').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      e.currentTarget.classList.add('hidden')
      projetoToDelete = null
    }
  })

  document.getElementById('projetos-grid').addEventListener('click', (e) => {
    const actionBtn = e.target.closest('[data-action]')
    if (!actionBtn) return
    const action = actionBtn.dataset.action
    const card = e.target.closest('.projeto-card')
    if (!card) return
    const id = parseInt(card.dataset.id)

    if (action === 'editar') {
      const projeto = projetos.find(p => p.id === id)
      if (projeto) abrirModalEdicao(projeto)
    }
    if (action === 'excluir') {
      projetoToDelete = id
      document.getElementById('confirm-dialog').classList.remove('hidden')
    }
  })
})
