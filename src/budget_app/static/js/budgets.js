async function loadBudgets() {
  try {
    const response = await fetch('/api/budgets', { credentials: 'include' });

    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }

    const data = await response.json();
    const err = data.message;
    const { budgets } = data; // object destructuring
    // const budgets = data.budgets;

    const list = document.getElementById('budgets-list');
    list.innerHTML = '';

    if (!response.ok)
      throw new Error(err || `Failed to load budgets (${response.status})`);

    if (!budgets || budgets.length === 0) {
      const budget_info = document.getElementById('empty_budgets');
      budget_info.style.display = 'inline';
      return;
    }

    budgets.forEach((budget) => {
      const li = document.createElement('li');

      // create anchor to /budget?id=ID
      const a = document.createElement('a');
      a.href = `/budget?id=${encodeURIComponent(budget.id)}`;
      a.textContent = `${budget.name} - ${budget.gross_income}`;
      a.setAttribute('aria-label', `View budget ${budget.name}`); // accessibility
      // TODO wondering if its bad practice to have html in the js?
      li.appendChild(a);
      list.appendChild(li);
    });
  } catch (err) {
    document.getElementById('error').textContent = err.message;
  }
}

document.addEventListener('DOMContentLoaded', loadBudgets);
