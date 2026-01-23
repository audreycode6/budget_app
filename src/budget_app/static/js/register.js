import { displayError, setFormDisabled } from './utils/ui.js';

/* =========================================================
   Constants
========================================================= */
const ELEMENT_IDS = {
  FORM: 'register-form',
  USERNAME: 'username',
  PASSWORD: 'password',
  ERROR: 'error',
};

const API_ENDPOINTS = {
  REGISTER: '/api/auth/register',
};

const PAGE_ROUTES = {
  LOGIN: '/login',
};

/* =========================================================
   Form Submission
========================================================= */

/**
 * Handles registration form submission
 */
async function handleRegister(e) {
  e.preventDefault();

  const form = e.target;
  const credentials = {
    username: document.getElementById(ELEMENT_IDS.USERNAME).value,
    password: document.getElementById(ELEMENT_IDS.PASSWORD).value,
  };

  // Show loading state
  setFormDisabled(form, true, {
    loadingText: 'Creating account...',
    defaultText: 'Create Account',
  });
  displayError(ELEMENT_IDS.ERROR); // Clear previous errors

  try {
    const response = await fetch(API_ENDPOINTS.REGISTER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.message || 'Account creation failed');
    }

    // Store success message for login page to display
    localStorage.setItem(
      'successMessage',
      'Account created successfully! Please log in.'
    );

    window.location.href = PAGE_ROUTES.LOGIN;
  } catch (err) {
    console.error('Registration failed:', err);
    displayError(ELEMENT_IDS.ERROR, err.message || 'Failed to create account');
    setFormDisabled(form, false);
  }
}

/* =========================================================
   Initialization
========================================================= */

/**
 * Initializes the registration form
 */
function initializeRegisterForm() {
  const form = document.getElementById(ELEMENT_IDS.FORM);
  if (!form) return;

  form.addEventListener('submit', handleRegister);
}

document.addEventListener('DOMContentLoaded', initializeRegisterForm);
