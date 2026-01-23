document
  .getElementById('register-form')
  .addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        const err = data.message;
        throw new Error(err || 'Registeration failed');
      }

      // success
      window.location.href = '/login';

      // TODO flash/notify user that account is created
    } catch (err) {
      document.getElementById('error').textContent = err.message;
    }
  });
