import type { SongRecord, SongKey } from '../types'

/** 生成曲目唯一组合键: 曲名|ジャンル名(タイプ)|Lv */
export function makeSongKey(song: SongRecord): SongKey {
  return `${song['曲名']}|${song['ジャンル名(タイプ)']}|${song['Lv']}`
}

/** 从難易度字段提取文字分类 */
export function extractDiffCategory(難易度: string): string {
  if (!難易度) return 'なし'
  const m = 難易度.match(/^[^\(0-9]+/)
  if (m) return m[0].trim()
  // 纯数值難易度 (Lv46-50 部分条目)
  return '数値'
}
