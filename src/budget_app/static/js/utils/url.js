/**
 * Resolve budget ID from the current URL.
 *
 * Supported:
 *   /budget/35
 *   /budget/35/edit
 *   /budget?id=35   (legacy fallback)
 *
 * Returns: number | null
 */
export function getBudgetIdFromUrl() {
  const pathParts = window.location.pathname.split('/').filter(Boolean);

  // Path-based routing
  if (pathParts[0] === 'budget' && pathParts[1]) {
    const id = Number(pathParts[1]);
    return Number.isFinite(id) ? id : null;
  }

  // Legacy query-param fallback
  const q = new URLSearchParams(window.location.search).get('id');
  if (q !== null) {
    const id = Number(q);
    return Number.isFinite(id) ? id : null;
  }

  return null;
}
