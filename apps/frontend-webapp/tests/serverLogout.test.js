'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const { ServerLogout } = require('../shared/serverLogout.js');

function makeContext({ token = 'abc', fetchImpl } = {}) {
    const fetchCalls = [];
    const fetchMock = fetchImpl || ((url, opts) => {
        fetchCalls.push({ url, opts });
        return Promise.resolve({ ok: true, status: 200 });
    });
    const win = {
        location: { hostname: 'localhost' },
        fetch: fetchMock,
        grindx: {
            config: {},
            session: { getToken: () => token },
            api: { buildApiUrl: (endpoint) => `http://localhost:8002/v1${endpoint}` }
        }
    };
    return { win, fetchCalls };
}

test('notify envia POST /auth/logout com token Bearer', async () => {
    const { win, fetchCalls } = makeContext({ token: 'abc' });
    const sl = new ServerLogout({ window: win });
    await sl.notify();

    assert.equal(fetchCalls.length, 1);
    assert.equal(fetchCalls[0].url, 'http://localhost:8002/v1/auth/logout');
    assert.equal(fetchCalls[0].opts.method, 'POST');
    assert.match(fetchCalls[0].opts.headers.Authorization, /^Bearer abc$/);
    assert.equal(fetchCalls[0].opts.keepalive, true, 'deve usar keepalive para sobreviver à navegação');
});

test('notify é tolerante a falha de rede', async () => {
    const { win } = makeContext({ fetchImpl: () => Promise.reject(new Error('offline')) });
    const sl = new ServerLogout({ window: win });
    const result = await sl.notify();
    assert.equal(result, undefined, 'não deve lançar em falha de rede');
});

test('notify sem token não faz fetch', async () => {
    const { win, fetchCalls } = makeContext({ token: null });
    const sl = new ServerLogout({ window: win });
    await sl.notify();
    assert.equal(fetchCalls.length, 0);
});