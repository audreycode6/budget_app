export function restoreAccordionState({ budgetId, category, collapseEl }) {
  const key = `budget_${budgetId}_cat_${category}`;
  if (localStorage.getItem(key) === '1') {
    bootstrap.Collapse.getOrCreateInstance(collapseEl).show();
  }
}

export function bindAccordionPersistence({ budgetId, category, collapseEl }) {
  const key = `budget_${budgetId}_cat_${category}`;

  collapseEl.addEventListener('shown.bs.collapse', () =>
    localStorage.setItem(key, '1')
  );
  collapseEl.addEventListener('hidden.bs.collapse', () =>
    localStorage.setItem(key, '0')
  );
}
