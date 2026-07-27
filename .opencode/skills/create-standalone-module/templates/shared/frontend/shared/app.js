/**
 * GrindX App.js — Standalone Fallback
 *
 * No monorepo, apps/frontend-webapp/shared/app.js fornece o framework completo.
 * Este stub reproduz a API mínima necessária para módulos funcionarem standalone.
 *
 * API exposta: window.grindx.{config, storage, session, theme}
 */

(function() {
    'use strict';

    // Se já existe (GrindX shell), não sobrescrever
    if (window.grindx && window.grindx.session) return;

    var GRINDX_CONFIG = {
        DEFAULT_LANG: 'pt-BR',
        SUPPORTED_LANGS: ['pt-BR', 'en-US', 'es-ES']
    };

    // StorageManager — localStorage com cache
    var cache = {};
    var storage = {
        get: function(key, fallback) {
            if (cache[key] !== undefined) return cache[key];
            var val = localStorage.getItem(key);
            var resolved = val !== null ? val : (fallback || null);
            cache[key] = resolved;
            return resolved;
        },
        set: function(key, value) {
            localStorage.setItem(key, value);
            cache[key] = value;
        },
        remove: function(key) {
            localStorage.removeItem(key);
            delete cache[key];
        },
        getJson: function(key, fallback) {
            var val = this.get(key);
            if (!val) return fallback;
            try { return JSON.parse(val); } catch(e) { return fallback; }
        },
        setJson: function(key, value) {
            this.set(key, JSON.stringify(value));
        }
    };

    // SessionManager — tokens JWT
    var session = {
        getToken: function() { return storage.get('access_token'); },
        setTokens: function(tokens) {
            storage.set('access_token', tokens.accessToken);
            storage.set('refresh_token', tokens.refreshToken);
        },
        getUserProfile: function() { return storage.getJson('grindx_user_profile', {}); },
        setUserProfile: function(profile) { storage.setJson('grindx_user_profile', profile); },
        clear: function() {
            storage.remove('access_token');
            storage.remove('refresh_token');
            storage.remove('grindx_user_profile');
        }
    };

    // ThemeManager — dark/light mode
    var theme = {
        theme: storage.get('grindx_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
        toggle: function() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
            storage.set('grindx_theme', this.theme);
            this.apply();
        },
        apply: function() {
            document.documentElement.classList.remove('light-theme', 'dark-theme');
            if (document.body) document.body.classList.remove('light-theme', 'dark-theme');
            document.documentElement.classList.add(this.theme + '-theme');
            if (document.body) document.body.classList.add(this.theme + '-theme');
        }
    };
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { theme.apply(); });
    } else {
        theme.apply();
    }

    window.grindx = {
        config: GRINDX_CONFIG,
        storage: storage,
        session: session,
        theme: theme
    };
})();
