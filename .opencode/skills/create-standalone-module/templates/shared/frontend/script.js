// @ts-nocheck
// Estado
let items = [];
let editingId = null;

// Detectar contexto (session existe via app.js)
const _isGrindx = typeof window !== 'undefined' && window.grindx && window.grindx.session;

// Helper: fetch com auth automática
async function _fetch(url, options) {
    const headers = {};
    if (_isGrindx) {
        const token = window.grindx.session.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
    } else if (typeof API_KEY !== 'undefined') {
        headers['X-API-Key'] = API_KEY;
    }
    const response = await fetch(url, { ...options, headers: { ...headers, ...options?.headers } });
    return response.json();
}

// Helper: download de PDF/binário
function downloadFromUrl(url, filename) {
    if (_isGrindx) {
        const token = window.grindx.session.getToken();
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        fetch(url, { headers })
            .then(res => { if (!res.ok) throw new Error('Erro ao baixar'); return res.blob(); })
            .then(blob => {
                const blobUrl = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = blobUrl; a.download = filename;
                document.body.appendChild(a); a.click();
                setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(blobUrl); }, 1000);
            });
    } else {
        const queryChar = API_KEY ? (url.includes('?') ? '&' : '?') : '';
        const urlWithKey = API_KEY ? url + queryChar + 'api_key=' + API_KEY : url;
        const a = document.createElement('a');
        a.href = urlWithKey; a.download = filename;
        document.body.appendChild(a); a.click();
        setTimeout(() => document.body.removeChild(a), 1000);
    }
}

// API calls
const api = {
    async listar(page = 1, page_size = 20) {
        return _fetch('/{route_api}?page=' + page + '&page_size=' + page_size);
    },
    async criar(dados) {
        return _fetch('/{route_api}', {
            method: 'POST',
            body: JSON.stringify(dados),
            headers: { 'Content-Type': 'application/json' }
        });
    },
    async atualizar(id, dados) {
        return _fetch('/{route_api}/' + id, {
            method: 'PUT',
            body: JSON.stringify(dados),
            headers: { 'Content-Type': 'application/json' }
        });
    },
    async excluir(id) {
        return _fetch('/{route_api}/' + id, { method: 'DELETE' });
    }
};

// Render
function renderizar() {
    const tbody = document.getElementById('table-body');
    const empty = document.getElementById('empty-state');
    if (!items.length) {
        tbody.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }
    empty.classList.add('hidden');
    tbody.innerHTML = items.map(function(item) {
        return '<tr>' +
            '<td data-label="ID">' + item.id + '</td>' +
            '<td data-label="Nome">' + (item.nome || '') + '</td>' +
            '<td data-label="Ações">' +
                '<button class="btn-icon" data-action="edit" data-id="' + item.id + '" aria-label="Editar" title="Editar">&#9998;</button>' +
                '<button class="btn-icon" data-action="delete" data-id="' + item.id + '" aria-label="Excluir" title="Excluir">&#128465;</button>' +
            '</td>' +
        '</tr>';
    }).join('');
}

function abrirModal(item) {
    editingId = item ? item.id : null;
    document.getElementById('modal-title').textContent = editingId ? 'Editar {entity_name}' : 'Novo {entity_name}';
    document.getElementById('field-nome').value = item ? item.nome : '';
    document.getElementById('modal-entity').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modal-entity').style.display = 'none';
    document.getElementById('form-entity').reset();
    editingId = null;
}

// Handlers
async function handleSubmit() {
    var nome = document.getElementById('field-nome').value.trim();
    if (!nome) return;
    try {
        if (editingId) {
            await api.atualizar(editingId, { nome: nome });
        } else {
            await api.criar({ nome: nome });
        }
        fecharModal();
        items = await api.listar();
        renderizar();
    } catch (err) {
        console.error('Erro ao salvar:', err);
        alert('Erro ao salvar. Verifique os dados e tente novamente.');
    }
}

async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja desativar este registro?')) return;
    try {
        await api.excluir(id);
        items = await api.listar();
        renderizar();
    } catch (err) {
        console.error('Erro ao excluir:', err);
        alert('Erro ao excluir. Tente novamente.');
    }
}

// Init
document.addEventListener('DOMContentLoaded', async function() {
    try {
        items = await api.listar();
        renderizar();
    } catch (err) {
        console.error('Erro ao carregar dados:', err);
    }

    document.getElementById('btn-novo').addEventListener('click', function() { abrirModal(null); });
    document.getElementById('btn-close-modal').addEventListener('click', fecharModal);
    document.getElementById('btn-cancel').addEventListener('click', fecharModal);
    document.getElementById('btn-save').addEventListener('click', handleSubmit);

    document.getElementById('table-body').addEventListener('click', function(e) {
        var btn = e.target.closest('[data-action]');
        if (!btn) return;
        var action = btn.dataset.action;
        var id = Number(btn.dataset.id);
        if (action === 'edit') {
            var item = items.find(function(i) { return i.id === id; });
            if (item) abrirModal(item);
        } else if (action === 'delete') {
            handleDelete(id);
        }
    });
});
