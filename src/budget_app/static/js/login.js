document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const data = await response.json();
      const err = data.message;
      throw new Error(err || 'Login failed');
    }

    // success
    window.location.href = '/budgets';
  } catch (err) {
    document.getElementById('error').textContent = err.message;
  }
});
