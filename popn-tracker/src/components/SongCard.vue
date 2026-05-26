<script setup lang="ts">
import { computed, ref } from 'vue'
import type { SongRecord, LampStatus } from '../types'
import { extractDiffCategory } from '../utils/song'
import { LAMP_LABELS, LAMP_COLORS, LAMP_BG } from '../constants/lamp'
import LampPicker from './LampPicker.vue'

const props = defineProps<{
  song: SongRecord
  lamp: LampStatus
}>()

const emit = defineEmits<{
  setLamp: [status: LampStatus]
}>()

const pickerOpen = ref(false)

const diffCategory = computed(() => extractDiffCategory(props.song['難易度']))
const borderColor = computed(() => LAMP_COLORS[props.lamp])
const bgColor = computed(() => LAMP_BG[props.lamp])
const lampLabel = computed(() => LAMP_LABELS[props.lamp])

const lampBadgeStyle = computed(() => ({
  backgroundColor: LAMP_COLORS[props.lamp],
  color: '#fff',
}))

function onCardClick() {
  pickerOpen.value = true
}

function onPickerSelect(status: LampStatus) {
  emit('setLamp', status)
  pickerOpen.value = false
}
</script>

<template>
  <div
    class="song-card"
    :style="{
      borderLeft: `4px solid ${borderColor}`,
      backgroundColor: bgColor,
    }"
  >
    <div class="card-main" @click="onCardClick">
      <div class="card-top">
        <span class="song-title" @click.stop>{{ song['曲名'] }}</span>
        <span class="lamp-badge" :style="lampBadgeStyle">{{ lampLabel }}</span>
      </div>
      <div class="card-meta">
        <span class="genre">{{ song['ジャンル名(タイプ)'] }}</span>
      </div>
      <div class="card-bottom">
        <span class="tag lv"><em>Lv</em>{{ song['Lv'] }}</span>
        <span class="tag gen"><em>代数</em>{{ song['代数'] }}</span>
        <span class="tag diff"><em>難易度</em>{{ diffCategory }}</span>
        <span v-if="song['bpm']" class="tag bpm"><em>BPM</em>{{ song['bpm'] }}</span>
        <span v-if="song['Notes']" class="tag notes"><em>Notes</em>{{ song['Notes'] }}</span>
      </div>
    </div>
    <LampPicker
      v-if="pickerOpen"
      :song-title="song['曲名']"
      :current="lamp"
      @select="onPickerSelect"
      @close="pickerOpen = false"
    />
  </div>
</template>

<style scoped>
.song-card {
  border-radius: 8px;
  margin: 4px 0;
  overflow: hidden;
  transition: background-color 0.2s, border-color 0.2s;
}
.card-main {
  padding: 10px 12px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}
.card-main:active {
  opacity: 0.85;
}
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.song-title {
  font-size: 15px;
  font-weight: 600;
  color: #f1f5f9;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  user-select: text;
  cursor: text;
}
.lamp-badge {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
  letter-spacing: 0.5px;
}
.card-meta {
  margin-top: 4px;
}
.genre {
  font-size: 12px;
  color: #94a3b8;
}
.card-bottom {
  display: flex;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.tag {
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 4px;
  font-weight: 500;
}
.tag em {
  font-style: normal;
  opacity: 0.65;
  font-size: 9px;
  margin-right: 2px;
  letter-spacing: 0;
}
.tag.lv {
  background: #1e3a5f;
  color: #38bdf8;
}
.tag.gen {
  background: #3b1764;
  color: #c084fc;
}
.tag.diff {
  background: #3f3f46;
  color: #d4d4d8;
}
.tag.notes {
  background: #1a2e1a;
  color: #86efac;
}
.tag.bpm {
  background: #2d1f0e;
  color: #fb923c;
}
</style>
