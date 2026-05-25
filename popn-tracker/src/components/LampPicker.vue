<script setup lang="ts">
import type { LampStatus } from '../types'
import { LAMP_LABELS, LAMP_COLORS, LAMP_STATUSES } from '../constants/lamp'

defineProps<{
  songTitle: string
  current: LampStatus
}>()

const emit = defineEmits<{
  select: [status: LampStatus]
  close: []
}>()

const options = LAMP_STATUSES
</script>

<template>
  <Teleport to="body">
    <div class="picker-overlay" @click.self="emit('close')">
      <div class="picker-panel">
        <div class="picker-title">{{ songTitle }}</div>
        <div class="picker-options">
          <button
            v-for="status in options"
            :key="status"
            class="picker-btn"
            :class="{ active: current === status }"
            :style="{
              borderColor: LAMP_COLORS[status],
              color: current === status ? '#fff' : LAMP_COLORS[status],
              backgroundColor: current === status ? LAMP_COLORS[status] : 'transparent',
            }"
            @click="emit('select', status)"
          >
            {{ LAMP_LABELS[status] }}
          </button>
        </div>
        <button class="picker-cancel" @click="emit('close')">取消</button>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.picker-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
.picker-panel {
  background: #1e293b;
  border-radius: 16px 16px 0 0;
  width: 100%;
  max-width: 640px;
  padding: 20px 16px 12px;
}
.picker-title {
  font-size: 14px;
  color: #94a3b8;
  text-align: center;
  margin-bottom: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 8px;
}
.picker-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}
/* NoPlay 占满整行 */
.picker-btn:first-child {
  grid-column: 1 / -1;
}
.picker-btn {
  padding: 14px 8px;
  border-radius: 10px;
  border: 2px solid;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
  letter-spacing: 0.3px;
}
.picker-cancel {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: none;
  background: #334155;
  color: #94a3b8;
  font-size: 14px;
  cursor: pointer;
}
</style>
