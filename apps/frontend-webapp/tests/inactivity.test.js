'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { InactivityTracker } = require('../shared/inactivity.js');

function fakeWindow() {
    const listeners = {};
    const selfRef = {};
    return {
        self: selfRef,
        top: selfRef,
        location: { origin: 'http://localhost:8101', href: '' },
        parent: { postMessage: () => {} },
        postMessage: () => {},
        CustomEvent: globalThis.CustomEvent,
        addEventListener: (type, fn) => {
            if (!listeners[type]) listeners[type] = [];
            listeners[type].push(fn);
        },
        removeEventListener: () => {},
        _listeners: listeners,
        _emit: (type, event) => {
            (listeners[type] || []).forEach((fn) => fn(event));
        }
    };
}

function fakeDoc() {
    const elements = {};
    return {
        readyState: 'complete',
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => true,
        createElement: (tag) => ({
            tagName: tag,
            className: '',
            innerHTML: '',
            style: {},
            setAttribute: () => {},
            addEventListener: () => {},
            querySelector: () => null,
            parentNode: { removeChild: () => {} }
        }),
        getElementById: (id) => elements[id] || null,
        body: {
            appendChild: (el) => { elements[el.id] = el; return el; }
        }
    };
}

test('armazena tempos de warning e logout configurados (30min)', () => {
    const tracker = new InactivityTracker({ autoInit: false });
    assert.equal(tracker.WARNING_TIME, 60000);
    assert.equal(tracker.LOGOUT_TIME, 1800000);
});

test('detecta contexto de janela principal (self === top)', () => {
    const win = fakeWindow();
    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: true
    });
    tracker.destroy();
    assert.equal(tracker.isIframe, false);
});

test('detecta contexto de iframe (self !== top)', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};
    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: true
    });
    tracker.destroy();
    assert.equal(tracker.isIframe, true);
});

test('em iframe, onActivity transmite postMessage ao pai e não reinicia timer', () => {
    let posted = null;
    const win = fakeWindow();
    win.self = { marker: 'iframe' };
    win.top = { marker: 'top' };
    win.parent = { postMessage: (data, origin) => { posted = { data, origin }; } };
    win.location = { origin: 'http://localhost:8101' };
    win.document = fakeDoc();

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false
    });

    const resetSpy = 0;
    tracker.onActivity();

    assert.equal(tracker.isIframe, true);
    assert.ok(posted, 'deve postar mensagem ao pai');
    assert.equal(posted.data.type, 'grindx-activity');
    assert.ok(posted.data.timestamp > 0);
    assert.equal(resetSpy, 0, 'não deve reiniciar timer próprio');
});

test('na janela principal, onActivity reinicia o timer', () => {
    const win = fakeWindow();
    win.location = { origin: 'http://localhost:8101' };

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false
    });

    tracker.lastActivity = 0;
    tracker.onActivity();
    tracker.destroy();
    assert.ok(tracker.lastActivity > 0, 'deve atualizar lastActivity');
});

test('evento message do tipo grindx-activity reinicia timer', () => {
    const win = fakeWindow();
    const doc = fakeDoc();

    const tracker = new InactivityTracker({
        window: win,
        document: doc,
        autoInit: true
    });

    tracker.lastActivity = 0;
    win._emit('message', {
        origin: 'http://localhost:8101',
        data: { type: 'grindx-activity' }
    });
    tracker.destroy();
    assert.ok(tracker.lastActivity > 0, 'mensagem deve reiniciar timer');
});

test('evento message de origem diferente é ignorado', () => {
    const win = fakeWindow();
    const doc = fakeDoc();

    const tracker = new InactivityTracker({
        window: win,
        document: doc,
        autoInit: true
    });

    tracker.lastActivity = 0;
    win._emit('message', {
        origin: 'http://evil.example',
        data: { type: 'grindx-activity' }
    });
    tracker.destroy();
    assert.equal(tracker.lastActivity, 0, 'origem diferente não deve resetar');
});

test('showConfirmationModal cria modal de confirmação', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false,
        i18n: { t: (k) => {
            const translations = {
                'inactivity_confirm': 'Você ainda está aí?',
                'inactivity_confirm_button': 'Sim, estou aqui!',
                'inactivity_seconds_remaining': 'segundos restantes'
            };
            return translations[k] || k;
        }}
    });

    tracker.showWarning();
    assert.equal(tracker.isWarningShown, true);
    assert.ok(tracker.modalElement, 'deve criar o elemento modal');
    tracker.destroy();
});

test('confirmPresence reinicia o timer e fecha o modal', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false
    });

    tracker.lastActivity = 0;
    tracker.modalElement = { parentNode: { removeChild: () => {} } };
    tracker.countdownInterval = setInterval(() => {}, 1000);

    tracker.confirmPresence();

    assert.ok(tracker.lastActivity > 0, 'deve atualizar lastActivity');
    assert.equal(tracker.modalElement, null, 'deve fechar o modal');
    assert.equal(tracker.countdownInterval, null, 'deve limpar o intervalo');
    tracker.destroy();
});

test('handleLogout chama onLogout quando fornecido', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};
    win.location = { origin: 'http://localhost:8101', href: '' };

    let loggedOut = false;
    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false,
        onLogout: () => { loggedOut = true; }
    });

    tracker.handleLogout();
    assert.equal(loggedOut, true);
});

test('sem onLogout, limpa sessão e redireciona para index.html', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};
    win.location = { origin: 'http://localhost:8101', href: '' };

    let cleared = false;
    const session = { clear: () => { cleared = true; } };

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false,
        session
    });

    tracker.handleLogout();
    assert.equal(cleared, true);
    assert.equal(win.location.href, 'index.html');
});

test('sem onLogout, com serverLogout disponível, notifica o servidor', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};
    win.location = { origin: 'http://localhost:8101', href: '' };

    let notified = false;
    globalThis.grindx = { serverLogout: { notify: () => { notified = true; } } };

    const session = { clear: () => {} };
    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false,
        session
    });

    tracker.handleLogout();
    assert.equal(notified, true, 'deve notificar o servidor no logout por inatividade');
    delete globalThis.grindx;
});

test('closeModal limpa modalElement e countdownInterval', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false
    });

    tracker.modalElement = { parentNode: { removeChild: () => {} } };
    tracker.countdownInterval = setInterval(() => {}, 1000);

    tracker.closeModal();

    assert.equal(tracker.modalElement, null, 'deve limpar modalElement');
    assert.equal(tracker.countdownInterval, null, 'deve limpar countdownInterval');
    tracker.destroy();
});

test('destroy limpa timers e fecha modal', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: true
    });

    tracker.modalElement = { parentNode: { removeChild: () => {} } };
    tracker.countdownInterval = setInterval(() => {}, 1000);

    tracker.destroy();

    assert.equal(tracker.timeoutId, null);
    assert.equal(tracker.warningTimeoutId, null);
    assert.equal(tracker.modalElement, null);
    assert.equal(tracker.countdownInterval, null);
});

test('resetTimer fecha modal existente', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false
    });

    tracker.modalElement = { parentNode: { removeChild: () => {} } };
    tracker.countdownInterval = setInterval(() => {}, 1000);

    tracker.resetTimer();

    assert.equal(tracker.modalElement, null);
    assert.equal(tracker.countdownInterval, null);
    tracker.destroy();
});
