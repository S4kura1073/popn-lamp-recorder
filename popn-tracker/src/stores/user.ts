import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SongRecord, SongKey, LampStatus } from '../types'
import { makeSongKey } from '../utils/song'
import {
  LAMP_STATUS_MIN,
  LAMP_STATUS_MAX,
  LAMP_STATUS_COUNT,
  DATA_VERSION,
  LEGACY_LAMP_MAX,
} from '../constants/lamp'

export const useUserStore = defineStore('user', () => {
  // ---- 点灯状态 ----
  const lampMap = ref<Record<SongKey, LampStatus>>({})

  function getLamp(song: SongRecord): LampStatus {
    return lampMap.value[makeSongKey(song)] ?? LAMP_STATUS_MIN
  }

  function cycleLamp(song: SongRecord) {
    const key = makeSongKey(song)
    const current = lampMap.value[key] ?? LAMP_STATUS_MIN
    lampMap.value[key] = ((current + 1) % LAMP_STATUS_COUNT) as LampStatus
  }

  function setLamp(song: SongRecord, status: LampStatus) {
    lampMap.value[makeSongKey(song)] = status
  }

  // ---- 曲目数据 ----
  const songs = ref<SongRecord[]>([])
  const songsLoaded = ref(false)

  async function loadSongs() {
    if (songsLoaded.value) return
    try {
      const resp = await fetch('/popn_difficulty_table.json')
      songs.value = await resp.json()
      songsLoaded.value = true
    } catch (e) {
      console.error('Failed to load song data', e)
    }
  }

  // ---- 统计 ----
  const stats = computed(() => {
    const total = songs.value.length
    let failed = 0
    let cleared = 0
    let fc = 0
    let perfect = 0
    for (const s of songs.value) {
      const lamp = lampMap.value[makeSongKey(s)] ?? LAMP_STATUS_MIN
      if (lamp >= 1) failed++    // Failed 及以上（即打过）
      if (lamp >= 2) cleared++   // NormalClear 及以上
      if (lamp >= 3) fc++        // FullCombo 及以上
      if (lamp >= LAMP_STATUS_MAX) perfect++   // Perfect
    }
    return { total, failed, cleared, fc, perfect }
  })

  // ---- 数据备份与恢复 ----
  // 导出格式: { [SongKey]: LampStatus, "__version": DATA_VERSION }
  function exportData(): string {
    const payload = { ...lampMap.value, __version: DATA_VERSION }
    return JSON.stringify(payload, null, 2)
  }

  function importData(jsonStr: string) {
    try {
      const data = JSON.parse(jsonStr)
      if (typeof data !== 'object' || data === null) throw new Error()

      const version = data.__version as number | undefined
      const entries = Object.entries(data).filter(([k]) => k !== '__version')

      const newMap: Record<SongKey, LampStatus> = {}
      for (const [key, val] of entries) {
        const n = Number(val)
        if (!Number.isInteger(n)) continue
        if (version === DATA_VERSION) {
          // 当前版本: 直接验证范围
          if (n >= LAMP_STATUS_MIN && n <= LAMP_STATUS_MAX) newMap[key] = n as LampStatus
        } else {
          // 旧版本迁移: 旧 0=Failed→1, 旧 1=NormalClear→2, 旧 2=FullCombo→3, 旧 3=Perfect→4
          if (n >= LAMP_STATUS_MIN && n <= LEGACY_LAMP_MAX) newMap[key] = (n + 1) as LampStatus
        }
      }
      lampMap.value = newMap
    } catch {
      throw new Error('无效的 JSON 数据')
    }
  }

  return {
    lampMap,
    getLamp,
    cycleLamp,
    setLamp,
    songs,
    songsLoaded,
    loadSongs,
    stats,
    exportData,
    importData,
  }
}, {
  persist: {
    pick: ['lampMap'],
    // localStorage 恢复后自动迁移旧版本数据 (v1: 0-3 → v2: 1-4)
    afterHydrate(ctx: import('pinia').PiniaPluginContext) {
      const map = ctx.store.lampMap as Record<SongKey, number>
      let needsMigration = false
      for (const val of Object.values(map)) {
        // 旧版本数据最大为 LEGACY_LAMP_MAX(3)，新版本最大为 LAMP_STATUS_MAX(4)
        // 旧版本无 NoPlay 概念，所有存在的值均 >= 1
        if (val > LAMP_STATUS_MIN && val <= LEGACY_LAMP_MAX) { needsMigration = true; break }
      }
      if (needsMigration) {
        const migrated: Record<SongKey, LampStatus> = {}
        for (const [key, val] of Object.entries(map)) {
          const n = Number(val)
          // 旧版本 1-3 全部加一；旧版本的 0 (Failed) 映射到新版本 1 (Failed)
          if (n > LAMP_STATUS_MIN && n <= LEGACY_LAMP_MAX)
            migrated[key] = (n + 1) as LampStatus
          else if (n === LAMP_STATUS_MIN)
            migrated[key] = 1 as LampStatus  // 旧 Failed(0) → 新 Failed(1)
          else
            migrated[key] = n as LampStatus
        }
        ctx.store.lampMap = migrated
      }
    },
  },
})
