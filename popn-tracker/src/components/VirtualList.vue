<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { SongRecord, LampStatus } from '../types'
import SongCard from './SongCard.vue'

const props = defineProps<{
  items: SongRecord[]
  getLamp: (song: SongRecord) => LampStatus
}>()

const emit = defineEmits<{
  setLamp: [song: SongRecord, status: LampStatus]
}>()

// 虚拟列表参数
const ITEM_HEIGHT = 82  // 每张卡片估计高度
const BUFFER = 5        // 上下缓冲项数
const containerRef = ref<HTMLElement | null>(null)
const scrollTop = ref(0)
const containerHeight = ref(600)

const totalHeight = computed(() => props.items.length * ITEM_HEIGHT)

const visibleRange = computed(() => {
  const start = Math.max(0, Math.floor(scrollTop.value / ITEM_HEIGHT) - BUFFER)
  const end = Math.min(
    props.items.length,
    Math.ceil((scrollTop.value + containerHeight.value) / ITEM_HEIGHT) + BUFFER
  )
  return { start, end }
})

const visibleItems = computed(() =>
  props.items.slice(visibleRange.value.start, visibleRange.value.end).map((song, i) => ({
    song,
    index: visibleRange.value.start + i,
  }))
)

function onScroll(e: Event) {
  scrollTop.value = (e.target as HTMLElement).scrollTop
}

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  if (containerRef.value) {
    containerHeight.value = containerRef.value.clientHeight
    resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        containerHeight.value = entry.contentRect.height
      }
    })
    resizeObserver.observe(containerRef.value)
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})
</script>

<template>
  <div ref="containerRef" class="virtual-list" @scroll="onScroll">
    <div class="virtual-list-inner" :style="{ height: totalHeight + 'px' }">
      <div
        class="virtual-list-content"
        :style="{ transform: `translateY(${visibleRange.start * ITEM_HEIGHT}px)` }"
      >
        <SongCard
          v-for="{ song, index } in visibleItems"
          :key="`${song['曲名']}-${song['ジャンル名(タイプ)']}-${song['Lv']}-${index}`"
          :song="song"
          :lamp="getLamp(song)"
          @set-lamp="(status) => emit('setLamp', song, status)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.virtual-list {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}
.virtual-list-inner {
  position: relative;
}
.virtual-list-content {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  padding: 0 8px;
}
</style>
