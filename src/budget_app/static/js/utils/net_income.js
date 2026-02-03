/**
 * Formats a budgets expenses and calculates total expenses
 * @param {dict}} totals - The budget object
 * @returns {number} The total expenses in budget
 */
export function getTotalExpenses(totals) {
  return totals.items.reduce((sum, item) => sum + parseFloat(item.total), 0);
}

/**
 * Calculates net income given gross income and total expenses
 * @param {number} grossIncome - The budgets gross income
 * @param {number} totalExpenses - The budgets total expenses
 * @returns {object} The net income and whether it is negative in budget
 */
export function calculateNetIncome(grossIncome, totalExpenses) {
  const netIncome = grossIncome - totalExpenses;
  const isInNegative = netIncome < 0;

  return { netIncome, isInNegative };
}
