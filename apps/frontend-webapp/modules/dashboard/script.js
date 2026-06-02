// === Constantes ===
const STATUS_CORES = {
    todo: '#94a3b8',
    'in-progress': '#3b82f6',
    done: '#22c55e',
}

const STATUS_LABELS = {
    todo: 'A Fazer',
    'in-progress': 'Em Progresso',
    done: 'Concluídas',
}

// === Estado ===
let dashboardData = null

// === API ===
async function carregarDashboard() {
    const res = await fetch('/v1/dashboard')
    if (!res.ok) throw new Error('Erro ao carregar dashboard')
    return res.json()
}

// === Render ===
function renderMetrics(data) {
    const grid = document.getElementById('metrics-grid')
    grid.innerHTML = ''
    const cards = [
        {
            label: 'Total de Projetos',
            value: data.metrics.total_projetos,
            sub: `${data.metrics.projetos_ativos} ativo${data.metrics.projetos_ativos !== 1 ? 's' : ''}`,
            navigate: 'projetos',
        },
        {
            label: 'Total de Tarefas',
            value: data.metrics.total_tarefas,
            sub: `${data.metrics.tarefas_concluidas} concluída${data.metrics.tarefas_concluidas !== 1 ? 's' : ''}`,
            navigate: 'tarefas',
        },
        {
            label: 'Recursos',
            value: data.metrics.total_recursos,
            sub: 'membros da equipe',
            navigate: 'recursos',
        },
        {
            label: 'Progresso Geral',
            value: `${data.metrics.progresso_geral}%`,
            sub: '',
            progress: data.metrics.progresso_geral,
        },
    ]
    cards.forEach(card => {
        const el = document.createElement('div')
        el.className = 'metric-card'
        if (card.navigate) {
            el.addEventListener('click', () => navegarPara(card.navigate))
        }
        el.innerHTML = `
            <div class="metric-card__header">
                <span class="metric-card__label">${card.label}</span>
            </div>
            <div class="metric-card__value">${card.value}</div>
            ${card.sub ? `<div class="metric-card__sub">${card.sub}</div>` : ''}
            ${card.progress !== undefined ? `
                <div class="metric-card__progress">
                    <div class="metric-card__progress-fill" style="width:${card.progress}%"></div>
                </div>
            ` : ''}
        `
        grid.appendChild(el)
    })
}

function renderStatus(data) {
    const grid = document.getElementById('status-grid')
    const { tarefas_a_fazer, tarefas_em_progresso, tarefas_concluidas, total_tarefas } = data.metrics

    grid.innerHTML = `
        <div class="card">
            <div class="card-title">Status das Tarefas</div>
            ${[
                { key: 'todo', count: tarefas_a_fazer },
                { key: 'in-progress', count: tarefas_em_progresso },
                { key: 'done', count: tarefas_concluidas },
            ].map(s => `
                <div class="status-item">
                    <div class="status-item__label">
                        <span class="status-dot" style="background:${STATUS_CORES[s.key]}"></span>
                        <span>${STATUS_LABELS[s.key]}</span>
                    </div>
                    <span class="badge badge--secondary">${s.count}</span>
                </div>
            `).join('')}
            <div class="status-bar">
                ${total_tarefas > 0 ? [
                    { key: 'todo', count: tarefas_a_fazer },
                    { key: 'in-progress', count: tarefas_em_progresso },
                    { key: 'done', count: tarefas_concluidas },
                ].filter(s => s.count > 0).map(s => `
                    <div class="status-bar__segment"
                         style="width:${(s.count / total_tarefas) * 100}%;background:${STATUS_CORES[s.key]}">
                    </div>
                `).join('') : ''}
            </div>
        </div>

        <div class="card">
            <div class="card-title">Próximos Prazos</div>
            ${data.proximos_prazos.length > 0 ? `
                <div>
                    ${data.proximos_prazos.map(p => `
                        <div class="prazo-item">
                            <div class="prazo-item__info">
                                <span class="project-dot" style="background:${p.project_color}"></span>
                                <span class="prazo-item__titulo">${p.titulo}</span>
                            </div>
                            <span class="badge ${p.dias_restantes <= 2 ? 'badge--destructive' : 'badge--secondary'}">
                                ${p.dias_restantes === 0 ? 'Hoje' : `${p.dias_restantes}d`}
                            </span>
                        </div>
                    `).join('')}
                </div>
            ` : '<div class="empty-state">Nenhum prazo próximo</div>'}
        </div>

        <div class="card">
            <div class="card-title">Alertas</div>
            ${data.tarefas_atrasadas.length > 0 ? `
                <div>
                    ${data.tarefas_atrasadas.map(t => `
                        <div class="alerta-item">
                            <div class="alerta-item__info">
                                <span class="project-dot" style="background:${t.project_color}"></span>
                                <span class="alerta-item__titulo">${t.titulo}</span>
                            </div>
                            <span class="badge badge--destructive">-${t.dias_atraso}d</span>
                        </div>
                    `).join('')}
                    ${data.total_tarefas_atrasadas > data.tarefas_atrasadas.length ? `
                        <p class="empty-state">+${data.total_tarefas_atrasadas - data.tarefas_atrasadas.length} tarefas atrasadas</p>
                    ` : ''}
                </div>
            ` : '<div class="success-message">Nenhuma tarefa atrasada</div>'}
        </div>
    `
}

function renderProjetos(data) {
    const section = document.getElementById('projetos-section')
    section.innerHTML = `
        <div class="card-title">Progresso dos Projetos</div>
        ${data.progresso_projetos.length > 0 ? `
            <div>
                ${data.progresso_projetos.map(p => `
                    <div class="projeto-item">
                        <div class="projeto-item__header">
                            <div class="projeto-item__info">
                                <span class="status-dot" style="background:${p.cor}"></span>
                                <span class="projeto-item__nome">${p.nome}</span>
                                <span class="badge badge--secondary">${p.total_tarefas} tarefas</span>
                            </div>
                            <span class="projeto-item__progress-text">${p.progresso}%</span>
                        </div>
                        <div class="projeto-item__bar">
                            <div class="projeto-item__fill" style="width:${p.progresso}%;background:${p.cor}"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        ` : '<div class="empty-state">Nenhum projeto cadastrado</div>'}
    `
}

function renderEquipe(data) {
    const section = document.getElementById('equipe-section')
    section.innerHTML = `
        <div class="card-title">Carga de Trabalho da Equipe</div>
        ${data.carga_trabalho.length > 0 ? `
            <div class="team-grid">
                ${data.carga_trabalho.map(c => {
                    const iniciais = c.nome.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
                    const primeiroNome = c.nome.split(' ')[0]
                    return `
                        <div class="team-card">
                            <div class="team-card__avatar" style="background:${c.cor}">${iniciais}</div>
                            <div>
                                <div class="team-card__name">${primeiroNome}</div>
                                <div class="team-card__counts">
                                    ${c.tarefas_ativas} ativa${c.tarefas_ativas !== 1 ? 's' : ''} /
                                    ${c.tarefas_concluidas} concluída${c.tarefas_concluidas !== 1 ? 's' : ''}
                                </div>
                            </div>
                        </div>
                    `
                }).join('')}
            </div>
        ` : '<div class="empty-state">Nenhum recurso alocado</div>'}
    `
}

// === Navegação ===
function navegarPara(modulo) {
    document.dispatchEvent(new CustomEvent('grindx:navigate', { detail: { view: modulo } }))
}

// === Init ===
async function init() {
    const loading = document.getElementById('loading')
    loading.classList.remove('hidden')
    try {
        dashboardData = await carregarDashboard()
        renderMetrics(dashboardData)
        renderStatus(dashboardData)
        renderProjetos(dashboardData)
        renderEquipe(dashboardData)
        loading.classList.add('hidden')
    } catch (err) {
        loading.textContent = 'Erro ao carregar dashboard'
        console.error(err)
    }
}

document.addEventListener('DOMContentLoaded', init)
