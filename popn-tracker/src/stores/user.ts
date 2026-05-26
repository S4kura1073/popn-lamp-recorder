import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SongRecord, SongKey, LampStatus } from '../types'
import { makeSongKey } from '../utils/song'
import {
  LAMP_STATUS_MIN,
  LAMP_STATUS_MAX,
  LAMP_STATUS_COUNT,
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
  function exportData(): string {
    return JSON.stringify(lampMap.value, null, 2)
  }

  function importData(jsonStr: string) {
    try {
      const data = JSON.parse(jsonStr)
      if (typeof data !== 'object' || data === null) throw new Error()

      const newMap: Record<SongKey, LampStatus> = {}
      for (const [key, val] of Object.entries(data)) {
        if (key === '__version') continue
        const n = Number(val)
        if (Number.isInteger(n) && n >= LAMP_STATUS_MIN && n <= LAMP_STATUS_MAX) {
          newMap[key] = n as LampStatus
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
  },
})
