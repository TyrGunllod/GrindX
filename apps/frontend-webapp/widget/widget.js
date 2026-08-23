/**
 * AGENTE IA — WIDGET FLUTUANTE (Mascote)
 *
 * Botão flutuante no canto do dashboard que abre um painel de chat nativo.
 * Chama POST /v1/agente/chat com o módulo ativo (body.dataset.activeModule).
 * URL do agente: configurável via window.__GRINDX_AGENT_URL no deploy.
 */
(function () {
    'use strict';

    const AGENT_URL = window.__GRINDX_AGENT_URL || 'http://localhost:8003';
    const CHAT_ENDPOINT = AGENT_URL.replace(/\/+$/, '') + '/v1/agente/chat';

    function getActiveModule() {
        return document.body.dataset.activeModule || '';
    }

    function getUserName() {
        const profile = (window.grindx && window.grindx.session && window.grindx.session.getUserProfile)
            ? window.grindx.session.getUserProfile()
            : {};
        return profile.nome_completo || profile.name || profile.username || profile.email || '';
    }

    function getGreeting() {
        const hour = new Date().getHours();
        if (hour >= 5 && hour < 12) return 'Bom dia';
        if (hour >= 12 && hour < 18) return 'Boa tarde';
        return 'Boa noite';
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
                '<span><img src="widget/grindx_chibi.png" class="grindx-ai-header-img" alt="" /> Assistente GrindX</span>' +
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
        const userName = getUserName();
        bubble.textContent = userName
            ? getGreeting() + ', ' + userName + '!'
            : getGreeting() + '!';
        document.body.appendChild(bubble);

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
