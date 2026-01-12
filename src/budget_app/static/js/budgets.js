async function loadBudgets() {
  try {
    const response = await fetch('/api/budgets');
    // TODO figure out if the path is valid?
    if (!response.ok) {
      throw new Error('Failed to load budgets.');
      // why error here when we do that in tests?
    }

    const budgets = await response.json();
    const list = document.getElementById('budgets-list');
    list.innerHTML = '';

    budgets.forEach((budget) => {
      const li = document.createElement('li');
      li.textContent = `${budget.name} - $${budget.total}`;
      list.appendChild(li);
    });
  } catch (err) {
    console.error(err);
    document.getElementById('budgets-list').innerHTML =
      '<li>Error loaidng budgets</li>';
  }
}

document.addEventListener('DOMContentLoaded', loadBudgets);
