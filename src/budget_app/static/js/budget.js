async function loadBudget() {
  const id = new URLSearchParams(window.location.search).get('id');
  const errorEl = document.getElementById('budget-error');

  if (!id) {
    errorEl.textContent = 'No budget id provided.';
    return;
  }

  try {
    const res = await fetch('/api/budget', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        budget_id: Number(id),
      }),
    });

    if (res.status === 401) {
      window.location.href = '/login';
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.message || `Failed (${res.status})`);
    }

    const budget = data.budget;

    document.getElementById(
      'budget-title'
    ).textContent = `Budget: "${budget.name}"`;
    document.getElementById(
      'budget-gross'
    ).textContent = `${budget.gross_income}`;
    document.getElementById(
      'budget-duration'
    ).textContent = `${budget.month_duration}`;

    const ul = document.getElementById('budget-items');
    ul.innerHTML = '';

    if (!budget.items || budget.items.length === 0) {
      const budget_items_info = document.getElementById('empty-budget-items');
      budget_items_info.style.display = 'inline';
      return;
    }

    budget.items.forEach((item) => {
      const li = document.createElement('li');
      li.textContent = `${item.name} — ${item.total}`;
      ul.appendChild(li);
    });
  } catch (err) {
    console.error(err);
    errorEl.textContent = err.message;
  }
}

document.addEventListener('DOMContentLoaded', loadBudget);
