<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from './stores/user'
import { extractDiffCategory } from './utils/song'
import { LAMP_STATUS_MIN, LAMP_STATUS_MAX } from './constants/lamp'
import type { LampStatus } from './types'
import FilterBar from './components/FilterBar.vue'
import VirtualList from './components/VirtualList.vue'
import ImportExport from './components/ImportExport.vue'

const store = useUserStore()

// 筛选状态
const filterLv = ref('')
const filterDiff = ref('')
const filterGen = ref('')
const filterLamp = ref('')

// 加载曲目数据
onMounted(() => {
  store.loadSongs()
})

// 筛选逻辑
const filteredSongs = computed(() => {
  return store.songs.filter(song => {
    if (filterLv.value && song['Lv'] !== filterLv.value) return false
    if (filterDiff.value && extractDiffCategory(song['難易度']) !== filterDiff.value) return false
    if (filterGen.value && song['代数'] !== filterGen.value) return false
    if (filterLamp.value !== '') {
      const lamp = store.getLamp(song)
      const target = +filterLamp.value as LampStatus
      if (lamp !== target) return false
    }
    return true
  })
})

// 统计信息
const statsDisplay = computed(() => {
  const s = store.stats
  const playedPct = s.total > 0 ? ((s.failed / s.total) * 100).toFixed(1) : '0.0'
  const clearPct  = s.total > 0 ? ((s.cleared / s.total) * 100).toFixed(1) : '0.0'
  return `打过: ${s.failed}/${s.total} (${playedPct}%)  CLEAR: ${s.cleared} (${clearPct}%)  FC: ${s.fc}  P: ${s.perfect}`
})
</script>

<template>
  <div class="app">
    <header class="app-header">
      <h1 class="title">popn-lamp-recorder</h1>
      <div class="stats">{{ statsDisplay }}</div>
    </header>

    <FilterBar
      :songs="store.songs"
      v-model:model-lv="filterLv"
      v-model:model-diff="filterDiff"
      v-model:model-gen="filterGen"
      v-model:model-lamp="filterLamp"
    />

    <div class="result-count">
      {{ filteredSongs.length }} 曲
    </div>

    <VirtualList
      v-if="store.songsLoaded"
      :items="filteredSongs"
      :get-lamp="store.getLamp"
      @set-lamp="(song, status) => store.setLamp(song, status)"
    />

    <div v-else class="loading">
      加载中...
    </div>

    <ImportExport />
  </div>
</template>

<style>
/* 全局样式 */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
html, body {
  height: 100%;
  background: #0f172a;
  color: #e2e8f0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  -webkit-font-smoothing: antialiased;
}
#app {
  height: 100%;
}
</style>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  max-width: 640px;
  margin: 0 auto;
}

.app-header {
  padding: 12px 12px 4px;
  flex-shrink: 0;
}
.title {
  font-size: 20px;
  font-weight: 800;
  color: #38bdf8;
  letter-spacing: -0.5px;
}
.stats {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.result-count {
  padding: 4px 12px;
  font-size: 12px;
  color: #64748b;
  flex-shrink: 0;
}

.loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 16px;
}
</style>
