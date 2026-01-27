// TODO figure out if this file is still needed

/**
 * Check authentication state by attempting to access a protected endpoint.
 * credentials: 'include' sends the session cookie. If it's valid, the endpoint
 * returns 200. If there's no session or it's expired, it returns 401/403.
 */
async function checkAuthState() {
  try {
    const res = await fetch('/api/auth/authenticated', {
      credentials: 'include',
    });
    return res.ok; // true if logged in (200), false if logged out (4xx)
  } catch (err) {
    console.error('Error checking auth state', err);
    return false;
  }
}
