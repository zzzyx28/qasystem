<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Search, Loading, MagicStick } from '@element-plus/icons-vue'
import { knowledgeQuery as queryApi, mutiRetriever } from '@/api'
import { ElMessage } from 'element-plus'

// —— 知识管理关键词检索 ——
const queryText = ref('')
const loading = ref(false)
const results = ref([])
const hasSearched = ref(false)

const search = async () => {
  const q = queryText.value?.trim()
  if (!q) {
    ElMessage.warning('请输入检索关键词')
    return
  }
  loading.value = true
  results.value = []
  hasSearched.value = true
  try {
    const { data } = await queryApi(q)
    const list = data?.results ?? data?.list ?? data?.data ?? (Array.isArray(data) ? data : [])
    results.value = list
    if (list.length === 0) ElMessage.info('未检索到相关结果')
  } catch (err) {
    ElMessage.error(err?.message || '检索失败')
    results.value = []
  } finally {
    loading.value = false
  }
}

// —— 向量可视化：演示用模拟 PCA 分布（不请求后端）——
const loadingVectors = ref(false)
const vectors = ref([])
const hoveredVector = ref(null)
const hoverPosition = ref({ x: 0, y: 0 })
const hoverTimeout = ref(null)
const vectorStats = ref(null)
const visualizationConfig = ref({
  pointSize: 8,
  showLabels: true
})
const canvasWrapper = ref(null)
const vectorCanvas = ref(null)

const uniqueClusters = computed(() => {
  if (!vectorStats.value?.clusterCounts) return []
  return Object.keys(vectorStats.value.clusterCounts)
})

const clusterCounts = computed(() => vectorStats.value?.clusterCounts || {})

const loadVectors = async () => {
  loadingVectors.value = true
  vectors.value = []
  hoveredVector.value = null
  await new Promise((r) => setTimeout(r, 400))
  vectors.value = generateMockVectors()
  vectorStats.value = computeVectorStats()
  await nextTick()
  visualizeVectors()
  ElMessage.success(`已加载演示向量 ${vectors.value.length} 条（模拟 PCA 聚类分布）`)
  loadingVectors.value = false
}

/** 确定性噪声，保证每次刷新分布稳定、簇清晰 */
function _demoNoise(i, salt = 0) {
  const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453123
  return x - Math.floor(x)
}

const generateMockVectors = () => {
  const sampleTexts = [
    'CBTC 列车自动控制系统在高峰期的运行策略与间隔优化。',
    '地铁制动系统故障时的应急处置流程与检修要点。',
    '轨道交通信号系统互联互通测试规范摘要。',
    '车辆段内调车作业安全规程与限速要求。',
    '接触网停电区间内的行车组织与乘客疏散预案。',
    '盾构隧道施工对邻近运营线路的沉降监测方法。',
    '站台门与车门联动故障时的降级运行模式说明。',
    '钢轨波磨检测周期及打磨验收标准（节选）。',
    '换乘站大客流管控与三级预警响应机制。',
    'FAO 全自动运行线路的远程复位与人工介入边界。'
  ]

  const centers = [
    { x: -0.82, y: 0.38 },
    { x: 0.15, y: 0.88 },
    { x: 0.92, y: 0.12 },
    { x: 0.42, y: -0.78 },
    { x: -0.48, y: -0.62 }
  ]

  const mockVectors = []
  let idx = 0
  const perCluster = 11
  const dim = 768

  centers.forEach((c, clusterId) => {
    for (let j = 0; j < perCluster; j++) {
      const spread = 0.11 + _demoNoise(idx) * 0.06
      mockVectors.push({
        id: idx,
        text: `${sampleTexts[idx % sampleTexts.length]}（演示簇 ${clusterId + 1} · 片段 ${j + 1}）`,
        metadata: { source: 'demo', cluster: clusterId },
        dimension: dim,
        position: {
          x: c.x + (_demoNoise(idx, 1) - 0.5) * 2 * spread,
          y: c.y + (_demoNoise(idx, 2) - 0.5) * 2 * spread
        },
        cluster: clusterId,
        similarity: 0.52 + clusterId * 0.065 + _demoNoise(idx, 3) * 0.06
      })
      idx += 1
    }
  })

  return mockVectors
}

const calculatePositionRange = () => {
  if (vectors.value.length === 0) return { minX: 0, maxX: 1, minY: 0, maxY: 1 }

  let minX = Infinity
  let maxX = -Infinity
  let minY = Infinity
  let maxY = -Infinity

  vectors.value.forEach((vector) => {
    if (vector.position) {
      minX = Math.min(minX, vector.position.x)
      maxX = Math.max(maxX, vector.position.x)
      minY = Math.min(minY, vector.position.y)
      maxY = Math.max(maxY, vector.position.y)
    }
  })

  if (minX === Infinity || maxX === -Infinity) {
    return { minX: -1, maxX: 1, minY: -1, maxY: 1 }
  }

  let paddingX = (maxX - minX) * 0.2
  let paddingY = (maxY - minY) * 0.2
  if (maxX - minX < 0.1) paddingX = 0.5
  if (maxY - minY < 0.1) paddingY = 0.5

  return {
    minX: minX - paddingX,
    maxX: maxX + paddingX,
    minY: minY - paddingY,
    maxY: maxY + paddingY
  }
}

const visualizeVectors = () => {
  if (!vectorCanvas.value || vectors.value.length === 0) return

  const canvas = vectorCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  if (canvasWrapper.value) {
    const rect = canvasWrapper.value.getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = 450
  } else {
    canvas.width = 800
    canvas.height = 450
  }

  const width = canvas.width
  const height = canvas.height
  ctx.clearRect(0, 0, width, height)

  const { minX, maxX, minY, maxY } = calculatePositionRange()
  const rangeX = Math.max(maxX - minX, 0.1)
  const rangeY = Math.max(maxY - minY, 0.1)
  const margin = 0.1

  vectors.value.forEach((vector, index) => {
    let x
    let y
    if (vector.position) {
      const normalizedX = (vector.position.x - minX) / rangeX
      const normalizedY = (vector.position.y - minY) / rangeY
      x = margin * width + normalizedX * (width * (1 - 2 * margin))
      y = margin * height + normalizedY * (height * (1 - 2 * margin))
    } else {
      x = Math.random() * width
      y = Math.random() * height
    }
    x = Math.max(10, Math.min(width - 10, x))
    y = Math.max(10, Math.min(height - 10, y))

    ctx.fillStyle = getVectorColor(vector)
    ctx.beginPath()
    ctx.arc(x, y, visualizationConfig.value.pointSize, 0, Math.PI * 2)
    ctx.fill()
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 2
    ctx.stroke()

    if (visualizationConfig.value.showLabels) {
      ctx.fillStyle = '#333'
      ctx.font = 'bold 12px Arial'
      ctx.textAlign = 'center'
      ctx.fillText((index + 1).toString(), x, y + 4)
    }
  })
}

const getVectorColor = (vector) => {
  if (vector.cluster !== undefined) {
    return getClusterColor(vector.cluster)
  }
  const similarity = vector.similarity || 0.5
  const hue = 240 - similarity * 120
  return `hsl(${hue}, 70%, 60%)`
}

const getClusterColor = (cluster) => {
  const colors = ['#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', '#118AB2', '#EF476F']
  return colors[Number(cluster) % colors.length] || '#999'
}

const handleCanvasHover = (event) => {
  if (!vectorCanvas.value || vectors.value.length === 0) return
  clearTimeout(hoverTimeout.value)

  const rect = vectorCanvas.value.getBoundingClientRect()
  const canvas = vectorCanvas.value
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const hoverRadius = visualizationConfig.value.pointSize + 5

  const { minX, maxX, minY, maxY } = calculatePositionRange()
  const rangeX = Math.max(maxX - minX, 0.1)
  const rangeY = Math.max(maxY - minY, 0.1)
  const margin = 0.1

  for (let i = 0; i < vectors.value.length; i++) {
    const vector = vectors.value[i]
    if (!vector.position) continue
    const normalizedX = (vector.position.x - minX) / rangeX
    const normalizedY = (vector.position.y - minY) / rangeY
    const pointX = margin * canvas.width + normalizedX * (canvas.width * (1 - 2 * margin))
    const pointY = margin * canvas.height + normalizedY * (canvas.height * (1 - 2 * margin))
    const distance = Math.sqrt((x - pointX) ** 2 + (y - pointY) ** 2)
    if (distance <= hoverRadius) {
      hoverTimeout.value = setTimeout(() => {
        hoveredVector.value = {
          ...vector,
          index: i,
          textPreview:
            vector.text?.substring(0, 150) + (vector.text?.length > 150 ? '...' : '')
        }
        hoverPosition.value = {
          x: Math.min(event.clientX + 20, window.innerWidth - 320),
          y: Math.max(event.clientY - 10, 20)
        }
      }, 100)
      return
    }
  }
  hoveredVector.value = null
}

const handleCanvasLeave = () => {
  clearTimeout(hoverTimeout.value)
  hoveredVector.value = null
}

const computeVectorStats = () => {
  if (vectors.value.length === 0) return null
  const clusters = new Set(vectors.value.map((v) => v.cluster).filter((c) => c !== undefined))
  const dimensions = vectors.value[0]?.dimension || 384
  const similarities = vectors.value.map((v) => v.similarity || 0.5)
  const avgSimilarity = similarities.reduce((sum, val) => sum + val, 0) / similarities.length
  const clusterCountsLocal = {}
  vectors.value.forEach((v) => {
    if (v.cluster !== undefined) {
      clusterCountsLocal[v.cluster] = (clusterCountsLocal[v.cluster] || 0) + 1
    }
  })
  return {
    total: vectors.value.length,
    dimensions,
    clusters: clusters.size,
    avgSimilarity,
    clusterCounts: clusterCountsLocal
  }
}

const redrawVisualization = () => {
  if (vectors.value.length > 0) visualizeVectors()
}

// —— 多源数据检索（图节点 VectorAddress → Milvus 片段，与后端 mutiRetriever 一致）——
const loadingMuti = ref(false)
const multiResults = ref([])

function normalizeMultiItem(item, index) {
  if (item && (item.vector_address != null || item.vector_content != null)) {
    return {
      ...item,
      vector_content: item.vector_content ?? item.content ?? '',
      metadata: item.metadata ?? null
    }
  }
  const text = item?.content ?? item?.vector_content ?? ''
  const addr = item?.database_id ?? item?.vector_address ?? ''
  return {
    node_id: item?.node_id ?? addr ?? index + 1,
    node_name: item?.node_name ?? item?.source ?? '',
    labels: item?.labels ?? [],
    vector_address: String(addr),
    slice_number: item?.index ?? item?.slice_number ?? 0,
    vector_content: text,
    content_length: text.length,
    database_id: item?.database_id,
    source: item?.source ?? '',
    metadata: item?.metadata ?? null,
    milvus_hit: item?.milvus_hit
  }
}

const loadMultiRetrieve = async () => {
  loadingMuti.value = true
  multiResults.value = []
  try {
    const { data } = await mutiRetriever()
    const raw = Array.isArray(data) ? data : data?.data ?? []
    if (!Array.isArray(raw)) {
      ElMessage.error('检索失败，返回格式异常')
      return
    }
    const list = raw.map((row, i) => normalizeMultiItem(row, i))
    multiResults.value = list
    ElMessage.success(`检索完成，共 ${list.length} 条`)
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err?.message || '检索失败')
  } finally {
    loadingMuti.value = false
  }
}

watch(
  () => [visualizationConfig.value.pointSize, visualizationConfig.value.showLabels],
  redrawVisualization,
  { deep: true }
)
</script>

<template>
  <div class="knowledge-query">
    <el-card class="search-card" shadow="hover">
      <div class="search-box">
        <el-input
          v-model="queryText"
          placeholder="输入关键词进行知识管理检索"
          size="large"
          clearable
          @keyup.enter="search"
        >
          <template #append>
            <el-button :loading="loading" :icon="Search" @click="search">
              检索
            </el-button>
          </template>
        </el-input>
      </div>
    </el-card>

    <el-card v-if="results.length > 0" class="results-card" shadow="hover">
      <template #header>
        <span>检索结果</span>
      </template>
      <div v-loading="loading" class="kb-results-list">
        <div
          v-for="(item, index) in results"
          :key="index"
          class="kb-result-item"
        >
          <div class="result-title">
            {{ item.title ?? item.name ?? item.content?.slice(0, 50) ?? '无标题' }}
          </div>
          <div class="result-content">
            {{ item.content ?? item.text ?? item.snippet ?? '-' }}
          </div>
          <div v-if="item.source" class="result-meta">
            {{ item.source }}
          </div>
        </div>
      </div>
    </el-card>

    <el-empty
      v-else-if="hasSearched && !loading && queryText?.trim() && results.length === 0"
      description="暂无检索结果"
    />

    <el-row :gutter="24" class="extend-row">
      <el-col :xs="24" :lg="12">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <span class="panel-title">向量可视化</span>
            <el-tag type="info" size="small" class="panel-tag">演示 · PCA 风格分布</el-tag>
          </template>
          <div class="visualization-container">
            <div class="visualization-controls">
              <el-button type="primary" :loading="loadingVectors" @click="loadVectors">
                加载向量
              </el-button>
              <div class="control-group">
                <div class="slider-with-label">
                  <span class="slider-label">点大小: {{ visualizationConfig.pointSize }}</span>
                  <el-slider
                    v-model="visualizationConfig.pointSize"
                    :min="2"
                    :max="20"
                    :step="1"
                    show-stops
                    class="viz-slider"
                    @input="redrawVisualization"
                  />
                </div>
              </div>
            </div>

            <div class="visualization-main">
              <div v-if="loadingVectors" class="viz-loading">
                <el-icon class="is-loading" :size="28"><Loading /></el-icon>
                <p>正在加载向量数据...</p>
              </div>

              <div v-else-if="vectors.length > 0" class="visualization-canvas-container">
                <div ref="canvasWrapper" class="canvas-wrapper">
                  <canvas
                    ref="vectorCanvas"
                    class="vector-canvas"
                    @mousemove="handleCanvasHover"
                    @mouseleave="handleCanvasLeave"
                  />
                  <div
                    v-if="hoveredVector"
                    class="vec-tooltip"
                    :style="{
                      left: hoverPosition.x + 'px',
                      top: hoverPosition.y + 'px'
                    }"
                  >
                    <div class="tooltip-inner">
                      <h4>文本片段 {{ hoveredVector.index + 1 }}</h4>
                      <div class="tooltip-text">
                        {{ hoveredVector.textPreview }}
                      </div>
                      <div class="tooltip-meta">
                        <span>向量维度: {{ hoveredVector.dimension }}</span>
                        <span>相似度: {{ (hoveredVector.similarity || 0).toFixed(3) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="uniqueClusters.length > 0" class="visualization-legend">
                  <div v-for="cluster in uniqueClusters" :key="cluster" class="legend-item">
                    <span
                      class="legend-color"
                      :style="{ backgroundColor: getClusterColor(cluster) }"
                    />
                    <span class="legend-label">簇 {{ cluster }}</span>
                    <span class="legend-count">({{ clusterCounts[cluster] || 0 }})</span>
                  </div>
                </div>
              </div>

              <div v-else class="viz-empty">
                <el-empty description="尚未加载演示向量">
                  <p class="empty-hint">点击「加载演示向量」查看模拟 PCA 聚类效果（轨道交通知识管理示例片段）</p>
                </el-empty>
              </div>
            </div>

            <div v-if="vectorStats" class="vector-stats">
              <el-row :gutter="12">
                <el-col :span="6" :xs="12">
                  <div class="stat-card">
                    <div class="stat-value">{{ vectorStats.total }}</div>
                    <div class="stat-label">总向量数</div>
                  </div>
                </el-col>
                <el-col :span="6" :xs="12">
                  <div class="stat-card">
                    <div class="stat-value">{{ vectorStats.dimensions ?? '-' }}</div>
                    <div class="stat-label">向量维度</div>
                  </div>
                </el-col>
                <el-col :span="6" :xs="12">
                  <div class="stat-card">
                    <div class="stat-value">{{ vectorStats.clusters ?? '-' }}</div>
                    <div class="stat-label">聚类数</div>
                  </div>
                </el-col>
                <el-col :span="6" :xs="12">
                  <div class="stat-card">
                    <div class="stat-value">{{ (vectorStats.avgSimilarity ?? 0).toFixed(3) }}</div>
                    <div class="stat-label">平均相似度</div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="panel-card" shadow="hover">
          <template #header>
            <span class="panel-title">多源数据检索</span>
          </template>
          <div class="multi-source">
            <div class="link-actions">
              <a
                class="link-pill link-pill--primary"
                href="http://localhost:7474/browser/"
                target="_blank"
                rel="noopener noreferrer"
              >
                图数据库管理
              </a>
              <a
                class="link-pill link-pill--success"
                href="http://10.126.62.88:5601/app/enterprise_search/elasticsearch"
                target="_blank"
                rel="noopener noreferrer"
              >
                文档数据库管理
              </a>
            </div>
            <div class="multi-actions">
              <el-button
                type="primary"
                :loading="loadingMuti"
                :icon="MagicStick"
                @click="loadMultiRetrieve"
              >
                查找向量库
              </el-button>
            </div>

            <div v-if="loadingMuti" class="multi-loading">
              <el-icon class="is-loading" :size="28"><Loading /></el-icon>
              <p>正在检索数据...</p>
            </div>

            <template v-else-if="multiResults.length > 0">
              <div class="multi-result-box">
                <p class="multi-result-heading">检索结果（共 {{ multiResults.length }} 条）</p>
                <div class="multi-results-list">
                  <div
                    v-for="(result, index) in multiResults"
                    :key="index"
                    class="multi-result-item"
                  >
                    <div class="multi-node-line">
                      <span class="node-id">节点 {{ result.node_id }}</span>
                      <span v-if="result.node_name" class="node-name">({{ result.node_name }})</span>
                    </div>
                    <div v-if="(result.labels || []).length" class="multi-field">
                      <span class="field-label">标签</span>
                      <span class="field-value">{{ (result.labels || []).join(', ') }}</span>
                    </div>
                    <div class="multi-field">
                      <span class="field-label">向量地址</span>
                      <code class="field-mono">{{ result.vector_address }}</code>
                    </div>
                    <div class="multi-field">
                      <span class="field-label">切片编号</span>
                      <span class="field-value strong">{{ result.slice_number }}</span>
                    </div>
                    <div v-if="result.source" class="multi-field">
                      <span class="field-label">来源</span>
                      <span class="field-value">{{ result.source }}</span>
                    </div>
                    <div
                      v-if="result.metadata && Object.keys(result.metadata).length"
                      class="multi-field block"
                    >
                      <span class="field-label">扩展字段</span>
                      <pre class="meta-json">{{ JSON.stringify(result.metadata, null, 2) }}</pre>
                    </div>
                    <div class="multi-field block">
                      <span class="field-label">向量内容</span>
                      <div class="vector-content-box">
                        {{
                          result.vector_content && result.vector_content.length > 200
                            ? result.vector_content.substring(0, 200) + '...'
                            : result.vector_content
                        }}
                        <span
                          v-if="result.vector_content && result.vector_content.length > 200"
                          class="content-len"
                        >
                          （共 {{ result.vector_content.length }} 字符）
                        </span>
                      </div>
                    </div>
                    <div v-if="result.content_length" class="content-foot">
                      内容长度: {{ result.content_length }} 字符
                    </div>
                    <el-divider v-if="index < multiResults.length - 1" class="multi-divider" />
                  </div>
                </div>
              </div>
            </template>
            <div v-else class="multi-placeholder">
              <el-empty description="点击「查找向量库」从图与文档库关联检索" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.knowledge-query {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.search-card,
.results-card,
.panel-card {
  border-radius: var(--card-radius);
}

.panel-card :deep(.el-card__header) {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-weight: 600;
  color: var(--gray-900);
}

.panel-title {
  font-size: 15px;
}

.panel-tag {
  margin-left: auto;
}

.search-box {
  :deep(.el-input-group__append) {
    padding: 0;
    .el-button {
      margin: 0;
      border-radius: 0 var(--button-radius) var(--button-radius) 0;
    }
  }
}

.kb-results-list {
  min-height: 80px;
}

.kb-result-item {
  padding: 16px 0;
  border-bottom: 1px solid var(--gray-200);
  &:last-child {
    border-bottom: none;
  }
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 8px;
}

.result-content {
  font-size: 14px;
  color: var(--gray-600);
  line-height: 1.6;
}

.result-meta {
  margin-top: 8px;
  font-size: 12px;
  color: var(--gray-500);
}

.extend-row {
  align-items: stretch;
}

/* 多源检索 */
.multi-source {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.link-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.link-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  border-radius: var(--button-radius);
  font-size: 14px;
  text-decoration: none;
  border: 1px solid;
  transition:
    background 0.15s,
    color 0.15s;
  &--primary {
    color: var(--primary-500, #409eff);
    border-color: var(--primary-500, #409eff);
    &:hover {
      background: rgba(64, 158, 255, 0.08);
    }
  }
  &--success {
    color: var(--el-color-success);
    border-color: var(--el-color-success);
    &:hover {
      background: rgba(103, 194, 58, 0.08);
    }
  }
}

.multi-actions {
  text-align: center;
}

.multi-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: var(--gray-600);
  p {
    margin-top: 10px;
  }
}

.multi-result-box {
  margin-top: 4px;
}

.multi-result-heading {
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 12px;
  font-size: 14px;
}

.multi-results-list {
  font-size: 13px;
  line-height: 1.5;
}

.multi-result-item {
  padding-bottom: 4px;
}

.multi-node-line {
  margin-bottom: 10px;
}

.node-id {
  color: var(--primary-500, #409eff);
  font-weight: 600;
}

.node-name {
  color: var(--gray-800);
  margin-left: 8px;
}

.multi-field {
  margin: 8px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
  &.block {
    flex-direction: column;
    align-items: stretch;
  }
}

.field-label {
  color: var(--gray-600);
  min-width: 72px;
  flex-shrink: 0;
}

.field-value {
  color: var(--gray-800);
  &.strong {
    font-weight: 600;
  }
}

.field-mono {
  font-family: ui-monospace, 'Consolas', monospace;
  font-size: 12px;
  color: var(--el-color-warning);
  word-break: break-all;
}

.vector-content-box {
  color: var(--gray-800);
  background: var(--gray-50);
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 3px solid var(--primary-500, #409eff);
  margin-top: 6px;
}

.content-len {
  color: var(--gray-500);
  font-size: 12px;
}

.content-foot {
  text-align: right;
  font-size: 12px;
  color: var(--gray-500);
  margin-top: 4px;
}

.multi-divider {
  margin: 16px 0;
}

.multi-placeholder {
  padding: 24px 0;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.meta-json {
  margin: 0;
  padding: 10px 12px;
  font-size: 12px;
  line-height: 1.45;
  background: var(--gray-100);
  border-radius: 6px;
  overflow-x: auto;
  max-height: 220px;
  color: var(--gray-800);
  border: 1px solid var(--gray-200);
}

/* 向量可视化 */
.visualization-container {
  .visualization-controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding: 14px 16px;
    background: var(--gray-50);
    border-radius: var(--card-radius);
    border: 1px solid var(--gray-200);
  }

  .control-group {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }

  .slider-with-label {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    min-width: 180px;
  }

  .slider-label {
    font-size: 12px;
    color: var(--gray-600);
    font-weight: 500;
  }

  .viz-slider {
    width: 200px;
  }

  .visualization-main {
    min-height: 420px;
    border: 1px solid var(--gray-200);
    border-radius: var(--card-radius);
    background: #fff;
    position: relative;
    margin-bottom: 16px;
  }

  .viz-loading {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    color: var(--gray-600);
    p {
      margin-top: 10px;
      font-size: 14px;
    }
  }

  .visualization-canvas-container {
    position: relative;
  }

  .canvas-wrapper {
    position: relative;
    height: 450px;
    overflow: hidden;
    cursor: crosshair;
    background: var(--gray-50);
    border-radius: 4px;
  }

  .vector-canvas {
    width: 100%;
    height: 100%;
    display: block;
  }

  .vec-tooltip {
    position: fixed;
    background: #fff;
    border: 1px solid var(--gray-300);
    border-radius: 8px;
    padding: 12px;
    max-width: 300px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    z-index: 1000;
    pointer-events: none;

    .tooltip-inner h4 {
      margin: 0 0 8px;
      color: var(--gray-900);
      font-size: 14px;
    }
    .tooltip-text {
      max-height: 200px;
      overflow-y: auto;
      font-size: 12px;
      line-height: 1.45;
      color: var(--gray-700);
      margin-bottom: 8px;
    }
    .tooltip-meta {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      font-size: 11px;
      color: var(--gray-500);
    }
  }

  .visualization-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px 14px;
    border-top: 1px solid var(--gray-200);
    background: var(--gray-50);
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--gray-700);
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .legend-count {
    color: var(--gray-500);
  }

  .viz-empty {
    min-height: 360px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }

  .empty-hint {
    margin-top: 8px;
    font-size: 13px;
    color: var(--gray-500);
    text-align: center;
  }

  .vector-stats {
    .stat-card {
      text-align: center;
      padding: 14px 10px;
      background: var(--gray-50);
      border-radius: 8px;
      border: 1px solid var(--gray-200);
    }
    .stat-value {
      font-size: 20px;
      font-weight: 600;
      color: var(--primary-500, var(--primary));
      margin-bottom: 4px;
    }
    .stat-label {
      font-size: 11px;
      color: var(--gray-600);
      letter-spacing: 0.3px;
    }
  }
}

@media (max-width: 991px) {
  .viz-slider {
    width: 100%;
    max-width: 280px;
  }
}
</style>
