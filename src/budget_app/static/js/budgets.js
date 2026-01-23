async function loadBudgets() {
  try {
    const response = await fetch('/api/budgets', { credentials: 'include' });

    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }

    const data = await response.json();
    const err = data.message;
    const { budgets } = data;

    const list = document.getElementById('budgets-list');
    list.innerHTML = '';

    if (!response.ok)
      throw new Error(err || `Failed to load budgets (${response.status})`);

    if (!budgets || budgets.length === 0) {
      const emptyBudgetsMessage = document.getElementById('empty_budgets');
      emptyBudgetsMessage.style.display = 'inline';
      return;
    }

    budgets.forEach((budget) => {
      const row = document.createElement('div');
      row.className =
        'list-group-item d-flex justify-content-between align-items-center';

      const info = document.createElement('div');
      info.innerHTML = `<div class="fw-semibold">${budget.name}</div>`;

      const actions = document.createElement('div');
      actions.innerHTML = `<a href="/budget/${encodeURIComponent(budget.id)}"
                            class="btn btn-sm btn-outline-primary"
                            aria-label="View budget ${budget.name}">
                            View
                          </a>
                        `;

      row.appendChild(info);
      row.appendChild(actions);
      list.appendChild(row);
    });
  } catch (err) {
    document.getElementById('error').textContent = err.message;
  }
}

document.addEventListener('DOMContentLoaded', loadBudgets);
