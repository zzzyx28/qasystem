<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Link, Refresh } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const iframeLoading = ref(true)
const iframeError = ref(false)
const iframeKey = ref(0)
const iframeSrc = ref('')
const difyWorkspaceUrl = ref('')

const onLoad = () => {
  iframeLoading.value = false
  iframeError.value = false
}

const onError = () => {
  iframeLoading.value = false
  iframeError.value = true
}

const openDify = () => difyWorkspaceUrl.value && window.open(difyWorkspaceUrl.value, '_blank', 'noopener,noreferrer')

const reloadIframe = () => {
  iframeLoading.value = true
  iframeError.value = false
  iframeKey.value += 1
}

onMounted(() => {
  if (route.query.denied === '1') {
    ElMessage.warning('您没有权限访问该功能')
    router.replace({ query: {} })
  }
  iframeSrc.value = 'http://10.126.62.88:8007/chatbot/83KOUCt19CPrpLZ6'
  try {
    difyWorkspaceUrl.value = new URL(iframeSrc.value).origin
  } catch {
    difyWorkspaceUrl.value = ''
  }
})
</script>

<template>
  <div class="chat-page">
    <div class="page-bg-deco" aria-hidden="true">
      <span class="circle circle-1"></span>
      <span class="circle circle-2"></span>
    </div>

    <div class="chat-layout">
      <header class="chat-toolbar">
        <div class="toolbar-title">
          <h1>智能问答</h1>
          <p>当前页面已切换为 Dify 嵌入模式</p>
        </div>
        <div class="toolbar-actions">
          <el-button plain :disabled="!difyWorkspaceUrl" @click="openDify">
            <el-icon><Link /></el-icon>
            打开 Dify 工作台
          </el-button>
          <el-button type="primary" @click="reloadIframe">
            <el-icon><Refresh /></el-icon>
            刷新会话
          </el-button>
        </div>
      </header>

      <section class="iframe-shell">
        <div v-if="iframeLoading && !iframeError" class="state-overlay">
          <el-icon class="is-loading" :size="38"><Loading /></el-icon>
          <span>正在加载 Dify 会话...</span>
        </div>
        <div v-else-if="iframeError" class="state-overlay">
          <span>加载失败，请检查网络后重试</span>
          <el-button type="primary" @click="reloadIframe">重新加载</el-button>
        </div>
        <iframe
          v-if="iframeSrc"
          :key="iframeKey"
          :src="iframeSrc"
          class="chat-iframe"
          frameborder="0"
          allow="microphone"
          @load="onLoad"
          @error="onError"
        />
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.chat-page {
  position: relative;
  height: calc(100vh - var(--nav-height));
  padding: 14px var(--padding-inline) 22px;
  overflow: hidden;
}

.page-bg-deco {
  pointer-events: none;
  position: absolute;
  inset: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.36;
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 280px;
  height: 280px;
  top: -80px;
  right: -40px;
  background: radial-gradient(circle at center, rgba(212, 175, 55, 0.35), rgba(212, 175, 55, 0));
}

.circle-2 {
  width: 220px;
  height: 220px;
  bottom: -60px;
  left: -50px;
  background: radial-gradient(circle at center, rgba(82, 82, 91, 0.3), rgba(82, 82, 91, 0));
}

.chat-layout {
  position: relative;
  z-index: 1;
  max-width: var(--content-max-width);
  margin: 0 auto;
  height: 100%;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 12px;
}

.chat-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: var(--card-radius);
  border: 1px solid #d4d4d8;
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(10px);
}

.toolbar-title h1 {
  margin: 0 0 4px;
  font-size: 22px;
  line-height: 1.2;
}

.toolbar-title p {
  margin: 0;
  color: var(--gray-600);
  font-size: 13px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.iframe-shell {
  position: relative;
  min-height: 0;
  border-radius: var(--card-radius-lg);
  border: 1px solid #d4d4d8;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.state-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(248, 248, 248, 0.95);
  color: var(--gray-700);
  font-size: 14px;
}

.chat-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

@media (max-width: 768px) {
  .chat-page {
    padding: 12px 16px 16px;
  }

  .chat-toolbar {
    padding: 14px;
    align-items: flex-start;
    flex-direction: column;
  }

  .toolbar-actions {
    width: 100%;
  }

  .toolbar-actions :deep(.el-button) {
    flex: 1;
  }
}
</style>
