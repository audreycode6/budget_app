import { displayError, setFormDisabled } from './utils/ui.js';

/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  FORM: 'login-form',
  USERNAME: 'username',
  PASSWORD: 'password',
  ERROR: 'error',
};

const API_ENDPOINTS = {
  LOGIN: '/api/auth/login',
};

const PAGE_ROUTES = {
  BUDGETS: '/budgets',
};

/* =========================================================
   Form Submission
========================================================= */

/**
 * Handles login form submission
 */
async function handleLogin(e) {
  e.preventDefault();

  const form = e.target;
  const credentials = {
    username: document.getElementById(ELEMENT_IDS.USERNAME).value,
    password: document.getElementById(ELEMENT_IDS.PASSWORD).value,
  };

  // Show loading state
  setFormDisabled(form, true, {
    loadingText: 'Logging in...',
    defaultText: 'Log In',
  });
  displayError(ELEMENT_IDS.ERROR); // Clear previous errors

  try {
    const response = await fetch(API_ENDPOINTS.LOGIN, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || 'Login failed');
    }

    window.location.href = PAGE_ROUTES.BUDGETS;
  } catch (err) {
    console.error('Login failed:', err);
    displayError(ELEMENT_IDS.ERROR, err.message || 'Failed to log in');
    setFormDisabled(form, false);
  }
}

/* =========================================================
   Initialization
========================================================= */

/**
 * Initializes the login form
 */
function initializeLoginForm() {
  const form = document.getElementById(ELEMENT_IDS.FORM);
  if (!form) return;

  form.addEventListener('submit', handleLogin);
}

document.addEventListener('DOMContentLoaded', initializeLoginForm);
