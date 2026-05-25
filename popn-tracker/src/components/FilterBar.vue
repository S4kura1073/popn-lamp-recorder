<script setup lang="ts">
import type { SongRecord } from '../types'
import { extractDiffCategory } from '../utils/song'
import { LAMP_LABELS, LAMP_STATUSES } from '../constants/lamp'

const props = defineProps<{
  songs: SongRecord[]
  modelLv: string
  modelDiff: string
  modelGen: string
  modelLamp: string
}>()

const emit = defineEmits<{
  'update:modelLv': [v: string]
  'update:modelDiff': [v: string]
  'update:modelGen': [v: string]
  'update:modelLamp': [v: string]
}>()

// 动态提取可选项
import { computed } from 'vue'

const lvOptions = computed(() => {
  const set = new Set(props.songs.map(s => s['Lv']))
  return ['', ...Array.from(set).sort((a, b) => +a - +b)]
})

const diffOptions = computed(() => {
  const set = new Set(props.songs.map(s => extractDiffCategory(s['難易度'])))
  return ['', ...Array.from(set).sort()]
})

const genOptions = computed(() => {
  const set = new Set(props.songs.map(s => s['代数']))
  const nums: string[] = []
  const others: string[] = []
  set.forEach(v => { /^\d+$/.test(v) ? nums.push(v) : others.push(v) })
  nums.sort((a, b) => +a - +b)
  others.sort()
  return ['', ...nums, ...others]
})

// 点灯筛选选项：从 LAMP_LABELS 动态生成，避免硬编码
const lampOptions = [
  { value: '', label: '全部' },
  ...LAMP_STATUSES.map(s => ({ value: String(s), label: LAMP_LABELS[s] })),
]
</script>

<template>
  <div class="filter-bar">
    <select
      :value="modelLv"
      @change="emit('update:modelLv', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">Lv: 全部</option>
      <option v-for="lv in lvOptions" :key="lv" :value="lv">Lv{{ lv }}</option>
    </select>

    <select
      :value="modelDiff"
      @change="emit('update:modelDiff', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">難易度: 全部</option>
      <option v-for="d in diffOptions" :key="d" :value="d">{{ d }}</option>
    </select>

    <select
      :value="modelGen"
      @change="emit('update:modelGen', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">代数: 全部</option>
      <option v-for="g in genOptions" :key="g" :value="g">{{ g }}</option>
    </select>

    <select
      :value="modelLamp"
      @change="emit('update:modelLamp', ($event.target as HTMLSelectElement).value)"
    >
      <option v-for="opt in lampOptions" :key="opt.value" :value="opt.value">
        点灯: {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.filter-bar {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 8px;
}
.filter-bar select {
  width: 100%;
  padding: 7px 6px;
  border-radius: 6px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 13px;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2394a3b8' d='M2 4l4 4 4-4'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  padding-right: 24px;
}
.filter-bar select:focus {
  outline: 2px solid #38bdf8;
  outline-offset: -1px;
}
</style>
