async function loadNav() {
  // load navbar HTML
  try {
    const navRes = await fetch('/static/partials/nav.html');
    if (!navRes.ok) {
      console.error('Failed to load nav partial', navRes.status);
      return;
    }
    document.getElementById('navbar').innerHTML = await navRes.text();
  } catch (err) {
    console.error('Error fetching nav partial', err);
    return;
  }

  // check auth state
  try {
    const res = await fetch('/api/health', { credentials: 'include' });
    const loggedIn = res.ok;
    const currentPath = window.location.pathname;

    document
      .querySelectorAll('[data-auth="logged-in"]')
      .forEach((el) => (el.hidden = !loggedIn));

    document
      .querySelectorAll('[data-auth="logged-out"]')
      .forEach((el) => (el.hidden = loggedIn));

    document.querySelectorAll('[data-path]').forEach((el) => {
      if (el.dataset.path === currentPath) {
        el.hidden = true;
      }
    });

    // attach logout handler if present
    const logout = document.getElementById('logout-link');
    if (logout) {
      logout.addEventListener('click', async (e) => {
        e.preventDefault();
        await fetch('/api/auth/logout', {
          method: 'GET',
          credentials: 'include',
        });
        // force refresh so nav reflects logged-out
        window.location.href = '/login';
      });
    }
  } catch (err) {
    console.error('Error checking auth for nav', err);
  }
}

document.addEventListener('DOMContentLoaded', loadNav);
