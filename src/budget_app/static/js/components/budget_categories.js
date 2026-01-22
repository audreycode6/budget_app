import { el } from '../utils/dom.js';

export function groupItemsByCategory(items) {
  const groups = {};
  items.forEach((item) => {
    if (!groups[item.category]) {
      groups[item.category] = { total: 0, items: [] };
    }
    groups[item.category].total += Number(
      item.total_raw ?? item.total_raw ?? 0
    );
    groups[item.category].items.push(item);
  });
  return groups;
}

export function formatCategoryLabel(cat) {
  return String(cat)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function buildCategoryAccordion({
  category,
  data,
  parentId = 'budget-categories',
}) {
  const categoryId = category.replace(/_/g, '-');
  const label = formatCategoryLabel(category);

  const header = el('h2', {
    class: 'accordion-header',
    id: `heading-${categoryId}`,
  });

  const button = el(
    'button',
    {
      class: 'accordion-button collapsed',
      type: 'button',
      'data-bs-toggle': 'collapse',
      'data-bs-target': `#collapse-${categoryId}`,
      'aria-expanded': 'false',
      'aria-controls': `collapse-${categoryId}`,
    },
    [
      el('div', { class: 'd-flex justify-content-between w-100 pe-3' }, [
        el('span', { text: label }),
        el('strong', { text: `$${data.total.toFixed(2)}` }),
      ]),
    ]
  );

  header.appendChild(button);

  const itemsList = el(
    'ul',
    { class: 'list-group list-group-flush' },
    data.items.map((item) =>
      el(
        'li',
        {
          class:
            'list-group-item d-flex justify-content-between align-items-center',
        },
        [
          el('span', { text: item.name }),
          el('div', { class: 'd-flex gap-2 align-items-center' }, [
            // formatted display total
            el('span', { text: item.total }),

            // Edit button (visible label)
            el(
              'button',
              {
                class: 'btn btn-sm btn-outline-secondary item-edit',
                'data-item-id': String(item.id),
                'data-item-name': item.name,
                'data-item-total': String(item.total_raw ?? item.total),
                'data-item-category': item.category,
                type: 'button',
                title: 'Edit item',
              },
              [el('span', { text: 'Edit' })]
            ),

            // Delete button (visible label)
            el(
              'button',
              {
                class: 'btn btn-sm btn-outline-danger item-delete',
                'data-item-id': String(item.id),
                type: 'button',
                title: 'Delete item',
              },
              [el('span', { text: 'Delete' })]
            ),
          ]),
        ]
      )
    )
  );

  const collapse = el(
    'div',
    {
      id: `collapse-${categoryId}`,
      class: 'accordion-collapse collapse',
      'aria-labelledby': `heading-${categoryId}`,
      // note: NO data-bs-parent so multiple can be open at once
    },
    [el('div', { class: 'accordion-body p-0' }, [itemsList])]
  );

  return el('div', { class: 'accordion-item' }, [header, collapse]);
}
