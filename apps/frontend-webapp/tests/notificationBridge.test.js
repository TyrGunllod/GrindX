'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { NotificationBridge } = require('../shared/notificationBridge.js');

function makeParent() {
    const calls = [];
    return {
        calls,
        postMessage: (data, origin) => calls.push({ data, origin })
    };
}

test('notifyMensagens envia postMessage ao pai em iframe', () => {
    const parent = makeParent();
    const bridge = new NotificationBridge({ parent, isIframe: true, origin: '*' });
    assert.equal(bridge.notifyMensagens(), true);
    assert.deepEqual(parent.calls[0].data, { type: 'grindx:mensagens-atualizar' });
});

test('navegarPara envia tipo e url', () => {
    const parent = makeParent();
    const bridge = new NotificationBridge({ parent, isIframe: true, origin: '*' });
    bridge.navegarPara('modules/estoque/index.html');
    assert.deepEqual(parent.calls[0].data, {
        type: 'grindx:navegar',
        url: 'modules/estoque/index.html'
    });
});

test('fora de iframe não envia nada', () => {
    const parent = makeParent();
    const bridge = new NotificationBridge({ parent, isIframe: false, origin: '*' });
    assert.equal(bridge.notifyMensagens(), false);
    assert.equal(parent.calls.length, 0);
});
