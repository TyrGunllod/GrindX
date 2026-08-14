# Inactivity System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a user inactivity detection system that shows warnings after 60s and logs out after 5 minutes of inactivity, with iframe support and i18n.

**Architecture:** Centralized InactivityTracker manages global timer and event listeners; TimeoutHandler handles warnings/logout; integrates with SessionManager for cleanup.

**Tech Stack:** Vanilla JS, GrindX shared modules (StorageManager, SessionManager), i18n translations.

---

### Task 1: Initialize Tracker

**Files:**
- Create: `docs/superpowers/plans/2026-08-15-inactivity-system.md` (this file)
- Modify: `shared/app.js:1-5`

- [ ] **Step 1: Write initialization code**
```javascript
// Inactivity tracking system
class InactivityTracker {
  constructor() {
    this.lastActivity = Date.now();
    this.timeoutId = null;
    this.WARNING_TIME = 60000; // 60s
    this.LOGOUT_TIME = 300000; // 5min
    this.isWarningShown = false;
    this.init();
  }

  init() {
    this.bindEvents();
    this.startTimer();
  }

  bindEvents() {
    // Global events
    ['mousemove', 'mousedown', 'keypress', 'scroll', 'touchstart'].forEach(evt => {
      document.addEventListener(evt, () => this.resetTimer(), true);
    });
    // Iframe events (postMessage)
    window.addEventListener('message', (e) => {
      if (e.data && e.data.type === 'grindx-activity') {
        this.resetTimer();
      }
    });
  }

  startTimer() {
    this.timeoutId = setTimeout(() => this.checkTimeout(), this.WARNING_TIME);
  }

  resetTimer() {
    clearTimeout(this.timeoutId);
    this.lastActivity = Date.now();
    this.isWarningShown = false;
    if (!this.timeoutId) {
      this.startTimer();
    }
  }

  checkTimeout() {
    const now = Date.now();
    const inactiveTime = now - this.lastActivity;
    
    if (inactiveTime >= this.WARNING_TIME && !this.isWarningShown) {
      this.showWarning();
      this.timeoutId = setTimeout(() => this.handleLogout(), this.LOGOUT_TIME - this.WARNING_TIME);
    } else if (inactiveTime >= this.LOGOUT_TIME) {
      this.handleLogout();
    }
  }

  showWarning() {
    this.isWarningShown = true;
    const msg = window.grindx.i18n.t('inactivity.warning') || 'Your session will end in 60 seconds';
    // Use existing notification system
    if (window.grindx.notification) {
      window.grindx.notification.showWarning(msg);
    } else {
      alert(msg);
    }
  }

  handleLogout() {
    clearTimeout(this.timeoutId);
    // Clear session via SessionManager
    if (window.grindx.session) {
      window.grindx.session.clear();
    }
    // Redirect to login
    window.location.href = '/index.html';
  }
}

// Initialize tracker on app load
document.addEventListener('DOMContentLoaded', () => {
  window.grindx.inactivityTracker = new InactivityTracker();
});
```

- [ ] **Step 2: Run initial test**
Run: `node -c shared/app.js` (syntax check)
Expected: No syntax errors

- [ ] **Step 3: Commit**
```bash
git add shared/app.js
git commit -m "feat: add InactivityTracker initialization"
```

### Task 2: Add Warning Translation

**Files:**
- Modify: `shared/i18n/translations.js` (if exists) or create
- Modify: `shared/app.js` (use translation)

- [ ] **Step 1: Add translation keys**
```javascript
// In shared/i18n/translations.js or similar
const TRANSLATIONS = {
  'pt-BR': {
    // ... existing
    'inactivity.warning': 'Sua sessão será encerrada em 60 segundos'
  },
  'en-US': {
    // ... existing
    'inactivity.warning': 'Your session will end in 60 seconds'
  },
  'es-ES': {
    // ... existing
    'inactivity.warning': 'Su sesión finalizará en 60 segundos'
  }
};
```

- [ ] **Step 2: Update InactivityTracker to use i18n**
```javascript
showWarning() {
  this.isWarningShown = true;
  const msg = window.grindx.i18n.t('inactivity.warning') || 
              'Your session will end in 60 seconds';
  // ... rest same
}
```

- [ ] **Step 3: Commit**
```bash
git add shared/i18n/translations.js shared/app.js
git commit -m "feat: add inactivity warning translations"
```

### Task 3: Implement Session Cleanup

**Files:**
- Modify: `shared/app.js` (handleLogout)
- Modify: `test/unit/test_inactivity.js`

- [ ] **Step 1: Enhance handleLogout**
```javascript
handleLogout() {
  clearTimeout(this.timeoutId);
  // Clear tokens and profile
  if (window.grindx.session) {
    window.grindx.session.clear();
  }
  // Clear any inactivity-specific storage
  window.localStorage.removeItem('inactivity_warning_shown');
  // Redirect
  window.location.href = '/index.html';
}
```

- [ ] **Step 2: Add unit test skeleton**
```javascript
describe('InactivityTracker', () => {
  let tracker;
  
  beforeEach(() => {
    jest.useFakeTimers();
    tracker = new InactivityTracker();
  });
  
  afterEach(() => {
    jest.useRealTimers();
  });
  
  test('should reset timer on activity', () => {
    tracker.resetTimer();
    expect(tracker.lastActivity).toBeCloseTo(Date.now(), -1);
  });
  
  test('should show warning after 60s', () => {
    // Mock showWarning
    tracker.showWarning = jest.fn();
    jest.advanceTimersByTime(60000);
    expect(tracker.showWarning).toHaveBeenCalled();
  });
  
  test('should logout after 5min', () => {
    tracker.handleLogout = jest.fn();
    jest.advanceTimersByTime(300000);
    expect(tracker.handleLogout).toHaveBeenCalled();
  });
});
```

- [ ] **Step 3: Run tests**
Run: `npm test -- test/unit/test_inactivity.js`
Expected: Tests pass

- [ ] **Step 4: Commit**
```bash
git add shared/app.js test/unit/test_inactivity.js
git commit -m "feat: add session cleanup and unit tests"
```

### Task 4: Iframe Communication Setup

**Files:**
- Modify: `shared/app.js` (postMessage handling)
- Create: `modules/base/script.js` (template for iframes)

- [ ] **Step 1: Add postMessage listener in tracker**
```javascript
bindEvents() {
  // ... existing
  // Listen for activity messages from iframes
  window.addEventListener('message', (e) => {
    // Only accept messages from same origin for security
    if (e.origin === window.location.origin) {
      if (e.data && e.data.type === 'grindx-activity') {
        this.resetTimer();
      }
    }
  });
}
```

- [ ] **Step 2: Create iframe activity broadcaster**
```javascript
// modules/base/script.js (to be included in all modules)
(function() {
  function broadcastActivity() {
    window.parent.postMessage({
      type: 'grindx-activity',
      timestamp: Date.now()
    }, window.location.origin);
  }
  
  // Broadcast on activity
  ['mousemove', 'mousedown', 'keypress', 'scroll', 'touchstart'].forEach(evt => {
    document.addEventListener(evt, broadcastActivity, true);
  });
  
  // Initial broadcast on load
  broadcastActivity();
})();
```

- [ ] **Step 3: Commit**
```bash
git add shared/app.js modules/base/script.js
git commit -m "feat: add iframe activity communication"
```

### Task 5: Integration Testing

**Files:**
- Create: `test/integration/test_inactivity.js`
- Modify: `shared/app.js` (if needed)

- [ ] **Step 1: Write integration test**
```javascript
describe('Inactivity System Integration', () => {
  let originalLocation;
  
  beforeEach(() => {
    originalLocation = window.location;
    window.location = { href: '' };
    jest.useFakeTimers();
  });
  
  afterEach(() => {
    window.location = originalLocation;
    jest.useRealTimers();
  });
  
  test('should logout after 5min of inactivity', () => {
    const tracker = new InactivityTracker();
    const logoutSpy = jest.spyOn(tracker, 'handleLogout');
    
    jest.advanceTimersByTime(300000);
    expect(logoutSpy).toHaveBeenCalled();
  });
  
  test('should reset timer on activity', () => {
    const tracker = new InactivityTracker();
    const resetSpy = jest.spyOn(tracker, 'resetTimer');
    
    // Simulate activity
    document.dispatchEvent(new Event('mousemove'));
    expect(resetSpy).toHaveBeenCalled();
  });
  
  test('should handle iframe messages', () => {
    const tracker = new InactivityTracker();
    const resetSpy = jest.spyOn(tracker, 'resetTimer');
    
    window.dispatchEvent(new MessageEvent('message', {
      data: { type: 'grindx-activity' },
      origin: window.location.origin
    }));
    
    expect(resetSpy).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run integration tests**
Run: `npm test -- test/integration/test_inactivity.js`
Expected: Tests pass

- [ ] **Step 3: Commit**
```bash
git add test/integration/test_inactivity.js
git commit -m "feat: add integration tests for inactivity system"
```

### Task 6: Final Verification

**Files:** None (verification only)

- [ ] **Step 1: Run full test suite**
Run: `npm test`
Expected: All tests pass (>=70% coverage)

- [ ] **Step 2: Manual verification steps**
1. Login to GrindX
2. Open developer console
3. Wait 61 seconds -> verify warning appears
4. Wait additional 4 minutes -> verify redirect to login
5. Test activity resets timer
6. Test iframe activity resets timer (open a module, interact)
7. Test i18n switching shows correct warning language

- [ ] **Step 4: Commit final**
```bash
git commit -m "feat: complete inactivity system implementation"
```
