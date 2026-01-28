const API_ENDPOINTS = {
  AUTHENTICATE: '/api/auth/authenticated',
  LOGOUT: '/api/auth/logout',
};

/**
 * Check authentication state by attempting to access a protected endpoint.
 * credentials: 'include' sends the session cookie. If it's valid, the endpoint
 * returns 200. If there's no session or it's expired, it returns 401/403.
 */
async function checkAuthState() {
  try {
    const res = await fetch(API_ENDPOINTS.AUTHENTICATE, {
      credentials: 'include',
    });
    return res.ok; // true if logged in (200), false if logged out (4xx)
  } catch (err) {
    console.error('Error checking auth state', err);
    return false;
  }
}

/**
 * Redirect to login if user is not authenticated
 */
async function requireAuth() {
  const isAuthenticated = await checkAuthState();
  if (!isAuthenticated) {
    // Store the current page so we can redirect back after login
    sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
    window.location.href = '/login';
    return false;
  }
  return true;
}

/**
 * Automatically check authentication for protected pages on page load.
 * This runs automatically when the module loads.
 */
async function initAuthCheck() {
  const protectedPages = [
    '/budgets',
    '/budget/',
    '/create_budget',
    '/create_budget_items',
    '/edit',
    '/delete_budget',
  ];

  const currentPath = window.location.pathname;

  // Check if current page is protected
  const isProtectedPage = protectedPages.some((path) =>
    currentPath.startsWith(path),
  );

  if (isProtectedPage) {
    const isAuth = await checkAuthState();
    if (!isAuth) {
      // Store intended destination for post-login redirect
      sessionStorage.setItem('redirectAfterLogin', currentPath);
      window.location.href = '/login';
      return false;
    }

    // Show content if authenticated
    showProtectedContent();
  }

  return true;
}

/**
 * Show protected content after authentication check passes
 */
function showProtectedContent() {
  // Try multiple selectors to find the main content container
  const app =
    document.getElementById('app') ||
    document.querySelector('[data-protected]') ||
    document.querySelector('.protected-content');

  if (app) {
    app.style.visibility = 'visible';
    app.classList.remove('auth-hidden');
  }
}

/**
 * Logout user and redirect to login
 */
async function logout() {
  try {
    await fetch(API_ENDPOINTS.LOGOUT, {
      method: 'GET',
      credentials: 'include',
    });
  } catch (err) {
    console.error('Error logging out', err);
  } finally {
    // Clear any stored redirect
    sessionStorage.removeItem('redirectAfterLogin');
    window.location.href = '/login';
  }
}

/**
 * Handle post-login redirect.
 * Call this after successful login to redirect user back to their intended page.
 */
function handlePostLoginRedirect() {
  const redirectPath = sessionStorage.getItem('redirectAfterLogin');
  sessionStorage.removeItem('redirectAfterLogin');

  // Default to /budgets if no redirect was stored
  window.location.href = redirectPath || '/budgets';
}

// Auto-initialize auth check when module loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAuthCheck);
} else {
  // DOM already loaded
  initAuthCheck();
}

// Export for use in other modules
export {
  checkAuthState,
  requireAuth,
  initAuthCheck,
  logout,
  handlePostLoginRedirect,
  showProtectedContent,
  API_ENDPOINTS,
};
