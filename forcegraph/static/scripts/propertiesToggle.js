export function initPropertyElement(property) {
  const header = property.querySelector('.properties-header');
  const value = property.querySelector('.properties-value');
  const icon = property.querySelector('.toggle-icon');
  const verticalLine = icon?.querySelector('.vertical-line');

  if (!header || !value || !icon || !verticalLine) return;

  header.addEventListener('click', () => {
    console.log('скрыл');
    value.classList.toggle('hidden');
    icon.classList.toggle('rotate');
    verticalLine.classList.toggle('hidden');
  });
}

export function initToggleAll(wrapper) {
  const container = wrapper.nextElementSibling;
  const iconProp = wrapper.querySelector('.toggle-icon-prop');

  if (container && container.classList.contains('properties-container')) {
    wrapper.addEventListener('click', () => {
      container.classList.toggle('hidden');

      if (iconProp) {
        iconProp.classList.toggle('rotate');
      }
    });
  }
}

export function initAllToggles() {
  document.querySelectorAll('.properties').forEach(initPropertyElement);
  document.querySelectorAll('.toggle-all-wrapper').forEach(initToggleAll);

  const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType !== 1) return;

        if (node.classList.contains('properties')) {
          initPropertyElement(node);
        }

        if (node.classList.contains('toggle-all-wrapper')) {
          initToggleAll(node);
        }
        node.querySelectorAll?.('.properties').forEach(initPropertyElement);
        node.querySelectorAll?.('.toggle-all-wrapper').forEach(initToggleAll);
      });
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}
