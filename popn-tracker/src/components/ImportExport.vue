<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { EXPORT_FILE_PREFIX } from '../constants/lamp'

const store = useUserStore()

function handleExport() {
  const data = store.exportData()
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  // 使用本地时区日期，避免 UTC 时区偏差导致日期偏移
  const now = new Date()
  const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  a.href = url
  a.download = `${EXPORT_FILE_PREFIX}-${dateStr}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function handleImport() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    try {
      const text = await file.text()
      store.importData(text)
      alert('数据导入成功！')
    } catch (e) {
      alert('导入失败: ' + (e instanceof Error ? e.message : '未知错误'))
    }
  }
  input.click()
}
</script>

<template>
  <div class="import-export">
    <button class="btn export-btn" @click="handleExport">导出数据</button>
    <button class="btn import-btn" @click="handleImport">导入数据</button>
  </div>
</template>

<style scoped>
.import-export {
  display: flex;
  gap: 8px;
  padding: 0 8px 8px;
}
.btn {
  flex: 1;
  padding: 8px 0;
  border: 1px solid #334155;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s;
  -webkit-tap-highlight-color: transparent;
}
.export-btn {
  background: #0f172a;
  color: #38bdf8;
}
.export-btn:active {
  background: #1e3a5f;
}
.import-btn {
  background: #0f172a;
  color: #c084fc;
}
.import-btn:active {
  background: #3b1764;
}
</style>
