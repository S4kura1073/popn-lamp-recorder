<script setup lang="ts">
import type { SongRecord } from '../types'
import { extractDiffCategory } from '../utils/song'
import { LAMP_LABELS, LAMP_STATUSES } from '../constants/lamp'
import { computed, ref, onMounted } from 'vue'

const props = withDefaults(defineProps<{
  songs: SongRecord[]
  modelLv: string
  modelDiff: string
  modelGen: string
  modelLamp: string
  modelSearch?: string
}>(), {
  modelSearch: '',
})

const emit = defineEmits<{
  'update:modelLv': [v: string]
  'update:modelDiff': [v: string]
  'update:modelGen': [v: string]
  'update:modelLamp': [v: string]
  'update:modelSearch': [v: string]
}>()

// 从 popn_version.json 加载代数排序，后续直接编辑该文件即可维护顺序
const versionOrder = ref<string[]>([])

onMounted(async () => {
  try {
    const res = await fetch('/popn_version.json')
    const data: Record<string, string> = await res.json()
    versionOrder.value = Object.keys(data)
  } catch (e) {
    console.warn('Failed to load popn_version.json', e)
  }
})

// 动态提取可选项
const lvOptions = computed(() => {
  const set = new Set(props.songs.map(s => s['Lv']))
  return ['', ...Array.from(set).sort((a, b) => +a - +b)]
})

const diffOptions = computed(() => {
  if (!props.modelLv) return []
  const set = new Set(
    props.songs
      .filter(s => s['Lv'] === props.modelLv)
      .map(s => extractDiffCategory(s['難易度']))
  )
  return Array.from(set).sort()
})

const genOptions = computed(() => {
  const existingSet = new Set(props.songs.map(s => s['代数']))

  if (versionOrder.value.length > 0) {
    // 按 popn_version.json 的 key 顺序排列，只保留数据中实际存在的代数
    const ordered = versionOrder.value.filter(k => existingSet.has(k))
    // 将数据中有但 version 文件未收录的代数追加到末尾
    const extra = Array.from(existingSet).filter(v => !versionOrder.value.includes(v)).sort()
    return ['', ...ordered, ...extra]
  }

  // 降级：version 文件未加载时的原始排序
  const nums: string[] = []
  const others: string[] = []
  existingSet.forEach(v => { /^\d+$/.test(v) ? nums.push(v) : others.push(v) })
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
      @change="(e) => {
        emit('update:modelLv', (e.target as HTMLSelectElement).value)
        emit('update:modelDiff', '')
      }"
    >
      <option value="">Lv: 全部</option>
      <option v-for="lv in lvOptions" :key="lv" :value="lv">Lv{{ lv }}</option>
    </select>

    <select
      :value="modelDiff"
      :disabled="!modelLv"
      @change="emit('update:modelDiff', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">難易度: {{ modelLv ? '全部' : '—' }}</option>
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

    <input
      class="search-input"
      type="search"
      placeholder="搜索曲名..."
      :value="modelSearch"
      @input="emit('update:modelSearch', ($event.target as HTMLInputElement).value)"
    />
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
.filter-bar select:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.search-input {
  grid-column: 1 / -1;
  width: 100%;
  padding: 7px 10px;
  border-radius: 6px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 13px;
}
.search-input::placeholder {
  color: #475569;
}
.search-input:focus {
  outline: 2px solid #38bdf8;
  outline-offset: -1px;
}
</style>
