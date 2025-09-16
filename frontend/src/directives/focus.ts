import { type ObjectDirective, type DirectiveBinding, nextTick } from 'vue'

interface FocusDirective extends ObjectDirective<HTMLElement> {
  mounted(el: HTMLElement, binding: DirectiveBinding<boolean>): void
}

const focusDirective: FocusDirective = {
  async mounted(el, binding) {
    if (binding.value === false) {
      return
    }
    await nextTick()
    let firstFocusableElement = getFirstFocusableElement(el)
    if (firstFocusableElement) {
      firstFocusableElement.focus()
      if (
        binding.arg === 'autoselect' &&
        (firstFocusableElement instanceof HTMLInputElement ||
          firstFocusableElement instanceof HTMLTextAreaElement)
      ) {
        firstFocusableElement.select()
      }
    }
  },
}

function getFirstFocusableElement(parent: HTMLElement): HTMLElement | null {
  if (!parent) {
    return null
  }
  const focusableSelector =
    'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

  if (parent.matches(focusableSelector)) {
    return parent
  }

  const focusableElements = parent.querySelectorAll<HTMLElement>(focusableSelector)
  return focusableElements.length > 0 ? focusableElements[0] : null
}

export default focusDirective
