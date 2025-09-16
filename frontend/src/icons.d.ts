declare module '~icons/lucide/*' {
  import type { FunctionalComponent, SVGAttributes } from 'vue'
  const component: FunctionalComponent<SVGAttributes & { class?: string | string[] | undefined }>
  export default component
}
