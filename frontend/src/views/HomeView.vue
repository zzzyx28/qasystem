<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChatDotRound,
  Document,
  MapLocation,
  Collection,
  ArrowRight,
  TrendCharts,
  MagicStick,
  Monitor
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { getDocuments, kgUpdateStatistics, listUsersApi } from '@/api'

const router = useRouter()
const auth = useAuthStore()

const goConsult = () => router.push('/chat')
const goKnowledge = () => router.push('/knowledge')
const goTo = (path) => router.push(path)

const stats = ref([
  { value: '--', label: '用户数量' },
  { value: '--', label: '文档数量' },
  { value: '7x24', label: '在线服务时长' },
  { value: '--', label: '图谱关系数' }
])

const signalItems = ['线路态势', '风险预警', '标准校验', '故障追因']

const quickQuestions = [
  '地铁列车制动系统故障如何处理？',
  'CBTC 系统在高峰期如何保障稳定性？',
  '常见轨道交通信号系统类型有哪些？',
  '请给出轨道交通设计规范查询入口'
]

const allFeatures = [
  {
    title: '智能问答',
    desc: '结合大模型与RAG，生成可追溯、可复核的专业答案。',
    icon: ChatDotRound,
    path: '/chat',
    requiresAdmin: false
  },
  {
    title: '知识检索',
    desc: '按语义与关键词双路径定位标准、规程与历史案例。',
    icon: Document,
    path: '/knowledge/query',
    requiresAdmin: true
  },
  {
    title: '组件管理',
    desc: '集中维护意图识别、图谱更新和答案生成链路。',
    icon: MapLocation,
    path: '/component',
    requiresAdmin: true
  },
  {
    title: '文档中心',
    desc: '沉淀国标、行标与企业内部资料，支持版本化管理。',
    icon: Collection,
    path: '/knowledge',
    requiresAdmin: true
  }
]

const features = computed(() =>
  allFeatures.filter((item) => !item.requiresAdmin || auth.isAdmin)
)

function formatMetric(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '--'
  return Number(value).toLocaleString('zh-CN')
}

function firstNumericValue(obj, keys) {
  if (!obj || typeof obj !== 'object') return null
  for (const key of keys) {
    if (typeof obj[key] === 'number') return obj[key]
  }
  return null
}

async function loadRealStats() {
  if (!auth.isAdmin) {
    stats.value = [
      { value: '--', label: '用户数量' },
      { value: '--', label: '文档数量' },
      { value: '7x24', label: '在线服务时长' },
      { value: '--', label: '图谱关系数' }
    ]
    return
  }

  const [usersRes, docsRes, kgRes] = await Promise.allSettled([
    listUsersApi(),
    getDocuments(),
    kgUpdateStatistics()
  ])

  const usersCount = usersRes.status === 'fulfilled' && Array.isArray(usersRes.value?.data)
    ? usersRes.value.data.length
    : null
  const docsCount = docsRes.status === 'fulfilled' && Array.isArray(docsRes.value?.data)
    ? docsRes.value.data.length
    : null

  const kgData = kgRes.status === 'fulfilled' ? (kgRes.value?.data || {}) : {}
  const relationCount =
    firstNumericValue(kgData, ['relationship_count', 'relationships', 'relation_count', 'edges']) ??
    firstNumericValue(kgData.statistics, ['relationship_count', 'relationships', 'relation_count', 'edges'])

  stats.value = [
    { value: formatMetric(usersCount), label: '用户数量' },
    { value: formatMetric(docsCount), label: '文档数量' },
    { value: '7x24', label: '在线服务时长' },
    { value: formatMetric(relationCount), label: '图谱关系数' }
  ]
}

watch(() => auth.isAdmin, () => {
  loadRealStats()
})

onMounted(() => {
  loadRealStats()
})
</script>

<template>
  <div class="home-view">
    <section class="hero-shell">
      <div class="hero-grid">
        <div class="hero-copy">
          <el-tag class="hero-badge" effect="plain">Enterprise Knowledge Assistant</el-tag>
          <h1 class="hero-title">
            面向轨道交通场景的
            <span class="title-highlight">下一代智能知识入口</span>
          </h1>
          <p class="hero-desc">
            从检索到推理，从规范到问答，统一在一个现代化工作界面中完成。支持高并发问询与专业知识沉淀，兼顾效率和可信度。
          </p>
          <div class="hero-actions">
            <el-button type="primary" class="action-button primary" @click="goConsult">
              <el-icon><MagicStick /></el-icon>
              立即体验智能问答
            </el-button>
            <el-button v-if="auth.isAdmin" class="action-button secondary" @click="goKnowledge">
              <el-icon><Monitor /></el-icon>
              进入知识库管理台
            </el-button>
          </div>
        </div>

        <div class="hero-panel">
          <div class="panel-head">
            <span class="dot dot-1" />
            <span class="dot dot-2" />
            <span class="dot dot-3" />
            <span class="panel-title">Realtime Assistant Console</span>
          </div>
          <div class="panel-body">
            <div class="signal-chip" v-for="item in signalItems" :key="item">
              <span class="signal-pulse" />
              <span>{{ item }}</span>
            </div>
            <div class="mock-chart">
              <div class="bar" v-for="n in 9" :key="n" :style="{ height: `${28 + (n % 4) * 14}px` }" />
            </div>
            <div class="panel-foot">
              <el-icon><TrendCharts /></el-icon>
              <span>多轮会话与知识命中持续优化中</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section bento">
      <div class="bento-grid">
        <article class="bento-card bento-main">
          <h3>核心能力矩阵</h3>
          <p>围绕问答、检索、组件和文档四大模块构建统一智能中台。</p>
          <div class="feature-list">
            <button
              v-for="item in features"
              :key="item.title"
              class="feature-item"
              type="button"
              @click="goTo(item.path)"
            >
              <span class="feature-icon">
                <el-icon><component :is="item.icon" /></el-icon>
              </span>
              <span class="feature-meta">
                <strong>{{ item.title }}</strong>
                <small>{{ item.desc }}</small>
              </span>
              <el-icon class="feature-arrow"><ArrowRight /></el-icon>
            </button>
          </div>
        </article>

        <article class="bento-card bento-quick">
          <h3>快速提问模板</h3>
          <div class="quick-list">
            <button
              v-for="q in quickQuestions"
              :key="q"
              type="button"
              class="quick-item"
              @click="goConsult"
            >
              <el-icon><ChatDotRound /></el-icon>
              <span>{{ q }}</span>
            </button>
          </div>
        </article>

        <article class="bento-card bento-kpi">
          <h3>运行指标</h3>
          <div class="kpi-grid">
            <div v-for="s in stats" :key="s.label" class="kpi-item">
              <span class="kpi-value">{{ s.value }}</span>
              <span class="kpi-label">{{ s.label }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.home-view {
  padding: 24px 0 84px;
}

.hero-shell {
  padding: 0 var(--padding-inline) 44px;
}

.hero-grid {
  max-width: var(--content-max-width);
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  gap: 22px;
}

.hero-copy,
.hero-panel {
  border-radius: var(--card-radius-lg);
  border: 1px solid #d4d4d8;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.hero-copy {
  padding: 44px;
}

.hero-badge {
  border-radius: 999px;
  border: 1px solid rgba(212, 175, 55, 0.45);
  color: var(--gray-800);
  background: rgba(255, 255, 255, 0.72);
  padding: 8px 14px;
  margin-bottom: 24px;
}

.hero-title {
  font-size: clamp(2.2rem, 4.4vw, 4rem);
  line-height: 1.07;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin-bottom: 20px;
}

.hero-desc {
  font-size: 16px;
  line-height: 1.7;
  color: var(--gray-600);
  max-width: 92%;
  margin-bottom: 30px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-panel {
  padding: 14px;
  box-shadow: var(--shadow-md);
}

.panel-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px 14px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-1 { background: #f87171; }
.dot-2 { background: #fbbf24; }
.dot-3 { background: #4ade80; }

.panel-title {
  margin-left: 4px;
  font-size: 12px;
  color: var(--gray-500);
  font-weight: 600;
}

.panel-body {
  border-radius: 20px;
  border: 1px solid #e4e4e7;
  padding: 18px;
  background: linear-gradient(165deg, rgba(23, 23, 23, 0.94), rgba(39, 39, 42, 0.94));
  color: #fafafa;
}

.signal-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 8px 8px 0;
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.signal-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.6);
  animation: pulse 1.8s infinite;
}

.mock-chart {
  margin: 16px 0 14px;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  height: 96px;
}

.bar {
  flex: 1;
  border-radius: 8px 8px 0 0;
  background: linear-gradient(180deg, var(--accent), rgba(212, 175, 55, 0.2));
}

.panel-foot {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
}

.section {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--padding-inline);
}

.bento-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  grid-template-areas:
    "main quick"
    "main kpi";
  gap: 18px;
}

.bento-card {
  border-radius: var(--card-radius);
  border: 1px solid #d4d4d8;
  background: rgba(255, 255, 255, 0.9);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.bento-card h3 {
  margin: 0 0 8px;
  font-size: 22px;
  letter-spacing: -0.02em;
}

.bento-card p {
  margin: 0 0 16px;
  color: var(--gray-600);
}

.bento-main { grid-area: main; }
.bento-quick { grid-area: quick; }
.bento-kpi { grid-area: kpi; }

.feature-list {
  display: grid;
  gap: 10px;
}

.feature-item {
  width: 100%;
  text-align: left;
  border: 1px solid #e4e4e7;
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  display: grid;
  grid-template-columns: 40px 1fr 20px;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: var(--transition-normal);
}

.feature-item:hover {
  transform: translateY(-2px);
  border-color: #a1a1aa;
  box-shadow: var(--shadow-md);
}

.feature-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(145deg, #171717, #52525b);
}

.feature-meta {
  display: grid;
  gap: 4px;
}

.feature-meta strong {
  font-size: 15px;
}

.feature-meta small {
  font-size: 12px;
  color: var(--gray-500);
}

.feature-arrow {
  color: var(--gray-600);
}

.quick-list {
  display: grid;
  gap: 10px;
}

.quick-item {
  border: 1px dashed #a1a1aa;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  color: var(--gray-800);
  cursor: pointer;
  transition: var(--transition-fast);
}

.quick-item:hover {
  border-color: #52525b;
  background: #fff;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.kpi-item {
  border-radius: 14px;
  background: linear-gradient(160deg, #171717, #27272a);
  color: #f5f5f5;
  padding: 14px;
}

.kpi-value {
  display: block;
  font-size: 28px;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 4px;
}

.kpi-label {
  font-size: 12px;
  color: #d4d4d8;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.55); }
  70% { box-shadow: 0 0 0 10px rgba(212, 175, 55, 0); }
  100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
}

@media (max-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }

  .bento-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "main"
      "quick"
      "kpi";
  }
}

@media (max-width: 768px) {
  .hero-shell,
  .section {
    padding-left: 20px;
    padding-right: 20px;
  }

  .hero-copy {
    padding: 26px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-actions :deep(.el-button) {
    width: 100%;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
