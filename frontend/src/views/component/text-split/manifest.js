import { DocumentCopy } from '@element-plus/icons-vue'

export const menuItem = {
  id: 'text-split',
  title: '文本切分组件',
  desc: '提供多策略文本切分能力。',
  icon: DocumentCopy,
  color: 'var(--primary-500)',
  route: 'text-split',
  requiresAdmin: true
}

export const route = {
  path: 'text-split',
  alias: 'nl2cypher',
  name: 'text-split',
  component: () => import('./index.vue'),
  meta: { title: '文本切分', requiresAdmin: true }
}
