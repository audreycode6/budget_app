// Constants
const ELEMENT_IDS = {
  NAVBAR: 'navbar',
  LOGOUT_LINK: 'logout-link',
};

const API_ENDPOINTS = {
  HEALTH: '/api/health',
  LOGOUT: '/api/auth/logout',
};

const STATIC_RESOURCES = {
  NAV_PARTIAL: '/static/partials/nav.html',
};

const SELECTORS = {
  LOGGED_IN: '[data-auth="logged-in"]',
  LOGGED_OUT: '[data-auth="logged-out"]',
  NAV_LINK: '[data-path]',
};

/**
 * Load the nav partial HTML into the navbar container
 */
async function loadNavHTML() {
  try {
    const res = await fetch(STATIC_RESOURCES.NAV_PARTIAL);
    if (!res.ok) {
      console.error('Failed to load nav partial', res.status);
      return false;
    }
    document.getElementById(ELEMENT_IDS.NAVBAR).innerHTML = await res.text();
    return true;
  } catch (err) {
    console.error('Error fetching nav partial', err);
    return false;
  }
}

/**
 * Check authentication state by attempting to access a protected endpoint.
 * credentials: 'include' sends the session cookie. If it's valid, the endpoint
 * returns 200. If there's no session or it's expired, it returns 401/403.
 */
async function checkAuthState() {
  try {
    const res = await fetch(API_ENDPOINTS.HEALTH, { credentials: 'include' });
    return res.ok; // true if logged in (200), false if logged out (4xx)
  } catch (err) {
    console.error('Error checking auth state', err);
    return false;
  }
}

/**
 * Update nav visibility based on logged-in/logged-out state
 */
function updateNavVisibility(loggedIn) {
  // Show/hide auth-specific sections
  document.querySelectorAll(SELECTORS.LOGGED_IN).forEach((el) => {
    el.hidden = !loggedIn;
  });

  document.querySelectorAll(SELECTORS.LOGGED_OUT).forEach((el) => {
    el.hidden = loggedIn;
  });
}

/**
 * Mark the current page link as active in the nav
 */
function markCurrentPage() {
  const currentPath = window.location.pathname;

  document.querySelectorAll(SELECTORS.NAV_LINK).forEach((el) => {
    if (el.dataset.path === currentPath) {
      el.classList.add('active');
      el.setAttribute('aria-current', 'page');
    }
  });
}

/**
 * Attach logout handler to the logout link if it exists
 */
function attachLogoutHandler() {
  const logoutLink = document.getElementById(ELEMENT_IDS.LOGOUT_LINK);
  if (!logoutLink) return;

  logoutLink.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      await fetch(API_ENDPOINTS.LOGOUT, {
        method: 'GET',
        credentials: 'include',
      });
    } catch (err) {
      console.error('Error logging out', err);
    } finally {
      // Always redirect to login, regardless of logout endpoint success
      window.location.href = '/login';
    }
  });
}

/**
 * Initialize the navigation bar: load HTML, check auth state,
 * update visibility, and attach event handlers
 */
async function initializeNav() {
  const navLoaded = await loadNavHTML();
  if (!navLoaded) return;

  const loggedIn = await checkAuthState();

  updateNavVisibility(loggedIn);
  markCurrentPage();
  attachLogoutHandler();
}

document.addEventListener('DOMContentLoaded', initializeNav);
