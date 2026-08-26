'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { MensagensWidget } = require('../shared/mensagensWidget.js');

function fakeClassList() {
    const classes = new Set();
    return {
        classes,
        add: (c) => classes.add(c),
        remove: (c) => classes.delete(c),
        toggle: (c, force) => {
            const show = force !== undefined ? force : !classes.has(c);
            if (show) classes.add(c); else classes.delete(c);
            return show;
        },
        contains: (c) => classes.has(c)
    };
}

function fakeEl() {
    return { textContent: '', classList: fakeClassList(), setAttribute() {} };
}

test('count 0 esconde badge e balão', async () => {
    const badge = fakeEl();
    const balloon = fakeEl();
    const widget = new MensagensWidget({
        badge, balloon,
        getUnread: async () => 0,
        autoInit: false
    });
    await widget.refresh();
    assert.equal(badge.textContent, '');
    assert.equal(badge.classList.contains('visible'), false);
    assert.equal(balloon.classList.contains('visible'), false);
});

test('count > 0 mostra badge e balão até marcar visto', async () => {
    const badge = fakeEl();
    const balloon = fakeEl();
    const widget = new MensagensWidget({
        badge, balloon,
        getUnread: async () => 3,
        autoInit: false
    });
    await widget.refresh();
    assert.equal(badge.textContent, '3');
    assert.equal(badge.classList.contains('visible'), true);
    assert.equal(balloon.classList.contains('visible'), true);

    widget.markSeen();
    assert.equal(balloon.classList.contains('visible'), false);
    assert.equal(badge.classList.contains('visible'), true, 'badge permanece visível');
});

test('refresh dispara onCountChange e nova mensagem reaparece balão', async () => {
    let unread = 2;
    const balloon = fakeEl();
    let lastCount = null;
    const widget = new MensagensWidget({
        badge: fakeEl(), balloon,
        getUnread: async () => unread,
        onCountChange: (c) => { lastCount = c; },
        autoInit: false
    });
    await widget.refresh();
    assert.equal(lastCount, 2);
    widget.markSeen();
    assert.equal(balloon.classList.contains('visible'), false);

    unread = 5;
    await widget.refresh();
    assert.equal(lastCount, 5);
    assert.equal(balloon.classList.contains('visible'), true, 'novo recado reaparece');
});
