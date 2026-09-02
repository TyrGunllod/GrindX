/**
 * AGENTE IA — WIDGET FLUTUANTE (Mascote)
 *
 * Botão flutuante no canto do dashboard que abre um painel de chat nativo.
 * Chama POST /v1/agente/chat com o módulo ativo (body.dataset.activeModule).
 * URL do agente: configurável via window.__GRINDX_AGENT_URL no deploy.
 */
(function () {
    'use strict';

    const AGENT_URL = window.__GRINDX_AGENT_URL
        || (location.hostname.indexOf('onrender.com') !== -1 ? 'https://agente-ia-gexd.onrender.com' : 'http://localhost:8003');
    const CHAT_ENDPOINT = AGENT_URL.replace(/\/+$/, '') + '/v1/agente/chat';

    function getActiveModule() {
        return document.body.dataset.activeModule || '';
    }

    function getUserName() {
        const sources = [];
        if (window.dashboard && window.dashboard.user) sources.push(window.dashboard.user);
        if (window.grindx && window.grindx.session && window.grindx.session.getUserProfile) {
            try { sources.push(window.grindx.session.getUserProfile() || {}); } catch (_) {}
        }
        if (window.parent && window.parent.grindx && window.parent.grindx.session && window.parent.grindx.session.getUserProfile) {
            try { sources.push(window.parent.grindx.session.getUserProfile() || {}); } catch (_) {}
        }
        // tenta extrair do JWT se ainda não tem perfil
        try {
            const token = window.grindx && window.grindx.session && window.grindx.session.getToken ? window.grindx.session.getToken() : null;
            if (token) {
                const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
                const data = JSON.parse(atob(payload));
                if (data) sources.push(data);
            }
        } catch (_) {}
        let full = '';
        for (const p of sources) {
            full = p.nome_completo || p.name || '';
            if (full) break;
        }
        if (!full) {
            for (const p of sources) {
                full = p.email || '';
                if (full) break;
            }
        }
        if (!full) return '';
        const parts = String(full).trim().split(/\s+/).filter(Boolean);
        if (parts.length <= 2) return full.trim();
        return parts[0] + ' ' + parts[parts.length - 1];
    }

    function getGreeting() {
        const hour = new Date().getHours();
        if (hour >= 5 && hour < 12) return 'Bom dia';
        if (hour >= 12 && hour < 18) return 'Boa tarde';
        return 'Boa noite';
    }

    function renderDropdownBadges(count) {
        document.querySelectorAll('[data-mensagens-badge]').forEach((el) => {
            el.textContent = count > 0 ? String(count) : '';
            el.classList.toggle('visible', count > 0);
        });
    }

    function createWidget() {
        const fab = document.createElement('button');
        fab.className = 'grindx-ai-fab';
        fab.type = 'button';
        fab.setAttribute('aria-label', 'Abrir assistente de IA');
        fab.innerHTML = '<img src="widget/grindx_chibi.png" alt="Assistente GrindX" />';

        const panel = document.createElement('div');
        panel.className = 'grindx-ai-panel';
        panel.setAttribute('aria-hidden', 'true');
        panel.innerHTML =
            '<div class="grindx-ai-panel-header">' +
                '<span><img src="widget/grindx_chibi_head.png" class="grindx-ai-header-img" alt="" /> Assistente GrindX</span>' +
                '<button type="button" class="grindx-ai-close" aria-label="Fechar">&times;</button>' +
            '</div>' +
            '<div class="grindx-ai-messages"></div>' +
            '<div class="grindx-ai-input">' +
                '<input type="text" class="grindx-ai-field" placeholder="Pergunte sobre esta tela..." aria-label="Sua pergunta" />' +
                '<button type="button" class="grindx-ai-send" aria-label="Enviar"><i class="fas fa-paper-plane" aria-hidden="true"></i></button>' +
            '</div>';

        document.body.appendChild(fab);
        document.body.appendChild(panel);

        const bubble = document.createElement('div');
        bubble.className = 'grindx-ai-bubble';
        bubble.setAttribute('aria-hidden', 'true');
        bubble.setAttribute('role', 'button');
        bubble.setAttribute('tabindex', '0');
        const helpText = 'Eu sou o GrindX, e estou aqui para te ajudar, qualquer dúvida me pergunte!';
        function getBubbleCount() {
            return (window.grindx.mensagens && typeof window.grindx.mensagens.count === 'number')
                ? window.grindx.mensagens.count
                : 0;
        }
        function buildBubbleText(count) {
            const userName = getUserName();
            let text = userName
                ? getGreeting() + ', ' + userName + '!\n' + helpText
                : getGreeting() + '!\n\n' + helpText;
            if (count > 0) {
                text += '\n\n' + (count === 1 ? 'Você tem 1 novo recado!' : 'Você tem ' + count + ' novos recados!');
            }
            return text;
        }
        function refreshBubble(countOverride) {
            const count = (typeof countOverride === 'number') ? countOverride : getBubbleCount();
            bubble.textContent = buildBubbleText(count);
            bubble.classList.toggle('has-recados', count > 0);
            return !!getUserName();
        }
        refreshBubble();
        document.body.appendChild(bubble);
        // atualiza quando o perfil carregar (dashboard faz fetch async)
        let bubbleRefreshTries = 0;
        const bubbleRefreshTimer = setInterval(() => {
            bubbleRefreshTries++;
            if (refreshBubble() || bubbleRefreshTries > 10) clearInterval(bubbleRefreshTimer);
        }, 800);
        window.addEventListener('message', (e) => {
            if (e.data === 'profile-saved') refreshBubble();
        });

        // ---- Contador de mensagens não lidas (Mensageiro) ----
        const unreadBadge = document.createElement('span');
        unreadBadge.className = 'grindx-ai-badge';
        unreadBadge.setAttribute('aria-hidden', 'true');
        fab.appendChild(unreadBadge);

        const mensagens = window.grindx.MensagensWidget
            ? new window.grindx.MensagensWidget({
                badge: unreadBadge,
                api: window.grindx.api,
                onCountChange: (count) => {
                    refreshBubble(count);
                    renderDropdownBadges(count);
                },
                onOpenRecados: () => {
                    if (window.dashboard && typeof window.dashboard.navigateToModule === 'function') {
                        window.dashboard.navigateToModule('modules/mensagens/index.html');
                    }
                }
            })
            : null;
        window.grindx.mensagens = mensagens;
        // Avisa o dashboard que o widget está pronto para receber refresh pós-login
        try { window.dispatchEvent(new CustomEvent('grindx:mensagens-ready')); } catch (_) {}
        // Garante verificação imediata também quando a aba volta a ficar visível após login
        try { if (mensagens) mensagens.refresh(); } catch (_) {}

        // Clicar no balão de greeting com recados pendentes abre o módulo de mensagens
        bubble.addEventListener('click', () => {
            if (getBubbleCount() > 0 && mensagens) mensagens.openRecados();
        });
        bubble.addEventListener('keydown', (e) => {
            if ((e.key === 'Enter' || e.key === ' ') && getBubbleCount() > 0 && mensagens) {
                e.preventDefault();
                mensagens.openRecados();
            }
        });

        let bubbleTimer = null;

        function showBubble() {
            if (panel.classList.contains('open')) return;
            bubble.classList.add('show');
            clearTimeout(bubbleTimer);
            bubbleTimer = setTimeout(function () {
                bubble.classList.remove('show');
            }, 6000);
        }

        function hideBubble() {
            clearTimeout(bubbleTimer);
            bubble.classList.remove('show');
        }

        const messages = panel.querySelector('.grindx-ai-messages');
        const field = panel.querySelector('.grindx-ai-field');
        const sendBtn = panel.querySelector('.grindx-ai-send');
        const closeBtn = panel.querySelector('.grindx-ai-close');

        function addMessage(text, role) {
            const bubble = document.createElement('div');
            bubble.className = 'grindx-ai-msg grindx-ai-msg-' + role;
            bubble.textContent = text;
            messages.appendChild(bubble);
            messages.scrollTop = messages.scrollHeight;
            return bubble;
        }

        function addSources(sources) {
            const line = document.createElement('div');
            line.className = 'grindx-ai-sources';
            line.textContent = 'Fontes: ' + sources
                .map(function (s) { return s.filename + ' — ' + s.title; })
                .join(' · ');
            messages.appendChild(line);
            messages.scrollTop = messages.scrollHeight;
        }

        async function ask(question) {
            const text = (question || '').trim();
            if (!text) return;
            addMessage(text, 'user');
            field.value = '';

            const thinking = addMessage('Pensando...', 'assistant');
            try {
                const response = await fetch(CHAT_ENDPOINT, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: text, module: getActiveModule() })
                });
                if (!response.ok) throw new Error('HTTP ' + response.status);
                const data = await response.json();
                thinking.remove();
                addMessage(data.answer, 'assistant');
                if (data.sources && data.sources.length) {
                    addSources(data.sources);
                }
            } catch (err) {
                thinking.remove();
                addMessage('Não foi possível falar com o assistente. Tente novamente.', 'assistant');
            }
        }

        sendBtn.addEventListener('click', function () { ask(field.value); });
        field.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') ask(field.value);
        });
        fab.addEventListener('click', function () {
            hideBubble();
            const open = panel.classList.toggle('open');
            panel.setAttribute('aria-hidden', String(!open));
            if (open) field.focus();
        });
        fab.addEventListener('mouseenter', showBubble);
        fab.addEventListener('mouseleave', hideBubble);
        setTimeout(showBubble, 1500);
        closeBtn.addEventListener('click', function () {
            panel.classList.remove('open');
            panel.setAttribute('aria-hidden', 'true');
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }
})();
