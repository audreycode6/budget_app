import { displayError, setFormDisabled } from './utils/ui.js';
import { handlePostLoginRedirect } from './services/auth.js';

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

    handlePostLoginRedirect();
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
 * Initializes the login form and displays any success messages
 */
function initializeLoginForm() {
  const form = document.getElementById(ELEMENT_IDS.FORM);
  if (!form) return;

  form.addEventListener('submit', handleLogin);

  const errorEl = document.getElementById(ELEMENT_IDS.ERROR);

  // Check for login message (from auth redirect)
  const loginMessage = sessionStorage.getItem('loginMessage');
  if (loginMessage && errorEl) {
    displayError(ELEMENT_IDS.ERROR, loginMessage, 'warning');
  }

  // Check for success message from previous page (e.g., after registration)
  const successMessage = localStorage.getItem('successMessage');
  if (successMessage) {
    // Display success message at top of page
    const errorEl = document.getElementById(ELEMENT_IDS.ERROR);
    if (errorEl) {
      displayError(ELEMENT_IDS.ERROR, successMessage, 'success');
    }
    // Clear the message so it doesn't show again
    localStorage.removeItem('successMessage');
  }
}

document.addEventListener('DOMContentLoaded', initializeLoginForm);
