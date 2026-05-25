/** pop'n music 曲目记录（对应 JSON 数据字段） */
export interface SongRecord {
  Lv: string
  代数: string
  标记: string
  'ジャンル名(タイプ)': string
  曲名: string
  bpm: string
  Time: string
  Notes: string
  難易度: string
}

/** 点灯状态: 0=NoPlay, 1=Failed, 2=NormalClear, 3=FullCombo, 4=Perfect */
export type LampStatus = 0 | 1 | 2 | 3 | 4

/** 组合键: 曲名|ジャンル名(タイプ)|Lv（保证唯一） */
export type SongKey = string
