document
  .getElementById('create-budget-form')
  .addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const gross_income = document.getElementById('gross_income').value;
    const month_duration = document.getElementById('month_duration').value;

    try {
      const response = await fetch('/api/budget/create', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, gross_income, month_duration }),
      });

      const data = await response.json();

      if (!response.ok) {
        const err = data.message;
        throw new Error(err || 'Budget creation failed');
      }

      // success
      const budgetId = data?.budget?.id;
      if (!budgetId) throw new Error('Missing budget id in response');

      window.location.href = `/budget/${budgetId}`;
    } catch (err) {
      document.getElementById('error').textContent = err.message;
    }
  });
