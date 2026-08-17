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
    return {
        readyState: 'complete',
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => true
    };
}

test('armazena tempos de warning e logout configurados', () => {
    const tracker = new InactivityTracker({ autoInit: false });
    assert.equal(tracker.WARNING_TIME, 60000);
    assert.equal(tracker.LOGOUT_TIME, 300000);
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

test('showWarning usa onClick/i18n e marca isWarningShown', () => {
    const win = fakeWindow();
    win.self = {};
    win.top = {};
    let warned = null;

    const tracker = new InactivityTracker({
        window: win,
        document: fakeDoc(),
        autoInit: false,
        i18n: { t: (k) => (k === 'inactivity_warning' ? 'Aviso traduzido' : k) },
        onWarning: (msg) => { warned = msg; }
    });

    tracker.showWarning();
    assert.equal(tracker.isWarningShown, true);
    assert.equal(warned, 'Aviso traduzido');
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