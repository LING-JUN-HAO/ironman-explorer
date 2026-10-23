/**
 * iThome 每年的組別名稱都不同，這裡歸成固定的主題方便跨年度篩選。
 * 新的一屆出現新組別時補進對照表；沒對到的歸「其他」，不會漏資料。
 */
export const THEMES = [
  { id: 'ai', label: 'AI', hue: 268, groups: ['AI & Data', 'AI/ ML & Data', 'AI Engineering', 'AI 自動化', '生成式 AI', 'Build on Google AI', 'ChatGPT & Codex', 'Claude AI', 'Vibe Coding'] },
  { id: 'web', label: '前端與 Web', hue: 205, groups: ['Modern Web', 'JavaScript', 'Vue.js', 'WordPress', 'Web 3'] },
  { id: 'software', label: '軟體開發', hue: 150, groups: ['Software Development', 'Python', 'Rust', 'Odoo'] },
  { id: 'cloud', label: '雲端與維運', hue: 28, groups: ['DevOps', 'Cloud Native', 'Kubernetes', 'Build on AWS', 'IT Operation'] },
  { id: 'mobile', label: '行動開發', hue: 330, groups: ['Mobile Development', 'Kotlin'] },
  { id: 'security', label: '資安', hue: 2, groups: ['Security', 'AI Security'] },
  { id: 'management', label: '管理與敏捷', hue: 48, groups: ['IT 管理', 'IT管理', 'Agile'] },
  { id: 'share', label: '佛心分享', hue: 178, groups: ['SideProject30'], prefix: '佛心分享' },
  { id: 'self', label: '自我挑戰', hue: 225, groups: ['自我挑戰組'] },
  { id: 'other', label: '其他', hue: 0, groups: ['影片教學'] },
] as const

export type ThemeId = (typeof THEMES)[number]['id']

/** 色相給 CSS 的 --hue 用；「其他」不帶色彩 */
export const themeById = new Map(THEMES.map(t => [t.id as ThemeId, t]))

const lookup = new Map<string, ThemeId>(THEMES.flatMap(t => t.groups.map(g => [g, t.id] as const)))

export function themeOf(group: string): ThemeId {
  if (group.startsWith('佛心分享')) return 'share'
  return lookup.get(group) ?? 'other'
}
