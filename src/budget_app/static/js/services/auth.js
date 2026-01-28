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
    window.location.href = '/login';
    return false;
  }
  return true;
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
    window.location.href = '/login';
  }
}

// Export for use in other modules
export { checkAuthState, requireAuth, logout, API_ENDPOINTS };
