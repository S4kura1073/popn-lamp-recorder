import type { LampStatus } from '../types'

/** 最小点灯状态值 */
export const LAMP_STATUS_MIN = 0 as LampStatus
/** 最大点灯状态值 */
export const LAMP_STATUS_MAX = 4 as LampStatus
/** 全部点灯状态的有序数组 */
export const LAMP_STATUSES: LampStatus[] = [0, 1, 2, 3, 4]
/** 状态总数 */
export const LAMP_STATUS_COUNT = LAMP_STATUSES.length

/** 导出文件版本号（每次点灯状态体系升级时递增） */
export const DATA_VERSION = 2
/** 旧版本 (v1) 点灯状态范围上限（旧版本无 NoPlay，取值 0-3） */
export const LEGACY_LAMP_MAX = 3
/** 导出备份文件名前缀 */
export const EXPORT_FILE_PREFIX = 'popn-tracker-backup'

export const LAMP_LABELS: Record<LampStatus, string> = {
  0: 'NoPlay',
  1: 'Failed',
  2: 'NormalClear',
  3: 'FullCombo',
  4: 'Perfect',
} as const

export const LAMP_COLORS: Record<LampStatus, string> = {
  0: '#4a5568',   // NoPlay      - 白灰色
  1: '#3d3d42',   // Failed      - 灰黑色
  2: '#a07040',   // NormalClear - 铜色
  3: '#a0a8b0',   // FullCombo   - 银色
  4: '#c8a838',   // Perfect     - 金色
} as const

export const LAMP_BG: Record<LampStatus, string> = {
  0: '#1e293b',   // NoPlay      - 深蓝灰
  1: '#16181c',   // Failed      - 深灰黑
  2: '#2a1a08',   // NormalClear - 深铜褐
  3: '#1a1e22',   // FullCombo   - 深银灰
  4: '#221a04',   // Perfect     - 深金棕
} as const
