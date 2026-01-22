export function el(tag, options = {}, children = []) {
  const element = document.createElement(tag);

  Object.entries(options).forEach(([key, value]) => {
    if (key === 'class') {
      element.className = value;
    } else if (key == 'text') {
      element.textContent = value;
    } else if (key.startsWith('data-')) {
      element.setAttribute(key, value);
    } else {
      element.setAttribute(key, value);
    }
  });

  children.forEach((child) => element.appendChild(child));
  return element;
}
