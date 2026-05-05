<script setup>
import { ref, onMounted, watch } from 'vue'
import { MagicStick, Loading, UploadFilled, Download } from '@element-plus/icons-vue'
import { textSplitHealthCheck, textSplitCharacter, textSplitRecursive, textSplitMarkdown, textSplitPython } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const healthStatus = ref(null)
const healthDetail = ref('')

// 当前选中的切分方式（下拉框）
const activeSubFeature = ref('split-char')

// 表单数据
const form = ref({
  splitText: ''
})

// 文件上传相关
const fileInput = ref(null)
const currentFile = ref(null)
const fileName = ref('')

// 结果数据
const splitResult = ref(null)

const splitMethodOptions = [
  { value: 'split-char', label: '按字符切分' },
  { value: 'split-recursive', label: '递归切分' },
  { value: 'split-markdown', label: 'Markdown 切分' },
  { value: 'split-python', label: 'Python 切分' }
]

// 监听切分方式切换
watch(activeSubFeature, () => {
  form.value.splitText = ''
  splitResult.value = null
  currentFile.value = null
  fileName.value = ''
})

// 健康检查
const checkHealth = async () => {
  healthStatus.value = null
  healthDetail.value = ''
  try {
    const { data } = await textSplitHealthCheck()
    if (data?.status === 'ok') {
      healthStatus.value = 'ok'
    } else {
      healthStatus.value = 'error'
      healthDetail.value = data?.detail || '模块未就绪'
    }
  } catch {
    healthStatus.value = 'error'
    healthDetail.value = '请检查后端是否启动并安装 algorithm/NL_to_cypher 依赖'
  }
}

// 文件上传处理
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const validTypes = ['text/plain', 'text/markdown', 'text/x-markdown', 'application/json']
  const fileExtension = file.name.split('.').pop().toLowerCase()
  const validExtensions = ['txt', 'md', 'markdown', 'json']
  
  if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
    ElMessage.error('请上传 txt、md 或 json 格式的文件')
    return
  }
  
  if (file.size > 10 * 1024 * 1024) { // 10MB
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  currentFile.value = file
  fileName.value = file.name
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    
    // 如果是 JSON 文件，尝试格式化显示
    if (file.type === 'application/json' || fileExtension === 'json') {
      try {
        const jsonData = JSON.parse(content)
        form.value.splitText = JSON.stringify(jsonData, null, 2)
      } catch (err) {
        form.value.splitText = content
        ElMessage.warning('JSON 文件格式错误，已按文本处理')
      }
    } else {
      form.value.splitText = content
    }
    
    ElMessage.success(`已加载文件: ${file.name} (${formatFileSize(file.size)})`)
  }
  
  reader.onerror = () => {
    ElMessage.error('文件读取失败')
  }
  
  reader.readAsText(file, 'UTF-8')
}

// 清除文件
const clearFile = () => {
  currentFile.value = null
  fileName.value = ''
  form.value.splitText = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 格式文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 下载切片结果为 JSON
const downloadSplitResult = () => {
  if (!splitResult.value) return
  
  const dataStr = JSON.stringify(splitResult.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  
  // 生成文件名
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const method = activeSubFeature.value.replace('split-', '')
  link.download = `text_split_${method}_${timestamp}.json`
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('切片结果已下载')
}

// 提交表单
const submit = async () => {
  const active = activeSubFeature.value
  
  // 检查是否有输入内容
  if (!form.value.splitText?.trim() && !currentFile.value) {
    ElMessage.warning('请输入文本或上传文件')
    return
  }

  if (active === 'split-char') {
    await submitSplitCharacter()
  } else if (active === 'split-recursive') {
    await submitSplitRecursive()
  } else if (active === 'split-markdown') {
    await submitSplitMarkdown()
  } else if (active === 'split-python') {
    await submitSplitPython()
  }
}

// 各种提交函数
const submitSplitRecursive = async () => {
  const text = form.value.splitText?.trim()
  if (!text) {
    ElMessage.warning('请输入要切分的文本或上传文件')
    return
  }
  loading.value = true
  splitResult.value = null
  try {
    const { data } = await textSplitRecursive(text)
    splitResult.value = data
    ElMessage.success('递归字符切分完成')
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err?.message || '递归字符切分失败')
    splitResult.value = null
  } finally {
    loading.value = false
  }
}

const submitSplitMarkdown = async () => {
  const text = form.value.splitText?.trim()
  if (!text) {
    ElMessage.warning('请输入要切分的文本或上传文件')
    return
  }
  loading.value = true
  splitResult.value = null
  try {
    const { data } = await textSplitMarkdown(text)
    splitResult.value = data
    ElMessage.success('Markdown 切分完成')
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err?.message || 'Markdown 切分失败')
    splitResult.value = null
  } finally {
    loading.value = false
  }
}

const submitSplitPython = async () => {
  const text = form.value.splitText?.trim()
  if (!text) {
    ElMessage.warning('请输入要切分的文本或上传文件')
    return
  }
  loading.value = true
  splitResult.value = null
  try {
    const { data } = await textSplitPython(text)
    splitResult.value = data
    ElMessage.success('Python 切分完成')
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err?.message || 'Python 切分失败')
    splitResult.value = null
  } finally {
    loading.value = false
  }
}

const submitSplitCharacter = async () => {
  const text = form.value.splitText?.trim()
  if (!text) {
    ElMessage.warning('请输入要切分的文本或上传文件')
    return
  }
  loading.value = true
  splitResult.value = null
  try {
    const { data } = await textSplitCharacter(text)
    splitResult.value = data
    ElMessage.success('字符切分完成')
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || err?.message || '字符切分失败')
    splitResult.value = null
  } finally {
    loading.value = false
  }
}

// 组件挂载
onMounted(() => {
  checkHealth()
})

</script>

<template>
  <div class="text-split-view">
    <div class="text-split-bg-deco">
      <span class="circle circle-1"></span>
      <span class="circle circle-2"></span>
    </div>

    <!-- 顶部标题与健康状态固定区域 -->
    <div class="text-split-header">
      <div class="header-left"></div>
      <div class="header-right">
        <h1 class="page-title">
          <span class="title-highlight">文本切片组件</span>
        </h1>
        <p class="page-desc">
          提供多策略文本切片能力。
        </p>
        <div v-if="healthStatus !== null" class="health-row">
          <span class="health-label">服务状态：</span>
          <el-tag v-if="healthStatus === 'ok'" type="success" size="small">正常</el-tag>
          <el-tooltip v-else :content="healthDetail" placement="bottom" :show-after="300">
            <el-tag type="danger" size="small">不可用</el-tag>
          </el-tooltip>
          <el-button link type="primary" size="small" @click="checkHealth">重新检测</el-button>
        </div>
        <!-- 新增组件功能说明卡片 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <span>组件功能说明</span>
          </template>
          <div class="info-content">
            <div class="section">
              <h4>功能概述</h4>
              <p>提供以下核心能力：</p>
              <ul>
                <li>文本按照多策略切片</li>
              </ul>
            </div>
            <div class="section">
              <h4>使用流程</h4>
              <ol>
                <li>通过下拉框选择切片方式</li>
                <li>输入文本或上传文件（txt/md/json）</li>
                <li>点击提交并查看结果</li>
                <li>切片结果可下载为 JSON 文件</li>
              </ol>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 主区域 -->
    <div class="text-split-inner">
      <div class="text-split-content">
        <el-card class="selector-card" shadow="never">
          <div class="selector-row">
            <span class="selector-label">切分方式</span>
            <el-select v-model="activeSubFeature" class="method-select" placeholder="请选择切分方式">
              <el-option
                v-for="option in splitMethodOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </div>
        </el-card>

        <!-- 字符切分功能 -->
        <el-card class="form-card" shadow="hover" v-if="activeSubFeature === 'split-char'">
          <template #header>
            <span>字符切分</span>
          </template>
          <el-form label-width="100px" class="text-split-form">
            <el-form-item label="输入方式">
              <div class="input-method-selector">
                <div class="file-upload-area">
                  <input
                    ref="fileInput"
                    type="file"
                    accept=".txt,.md,.markdown,.json"
                    @change="handleFileUpload"
                    style="display: none"
                  />
                  <el-button
                    type="primary"
                    :icon="UploadFilled"
                    @click="fileInput?.click()"
                    size="small"
                  >
                    上传文件
                  </el-button>
                  <span class="file-info" v-if="fileName">
                    {{ fileName }}
                    <el-button
                      type="danger"
                      text
                      size="small"
                      @click="clearFile"
                    >
                      清除
                    </el-button>
                  </span>
                  <span class="file-hint" v-else>
                    支持 txt, md, json 格式，最大 10MB
                  </span>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="或输入文本">
              <el-input
                v-model="form.splitText"
                type="textarea"
                :rows="8"
                placeholder="请输入要切分的文本内容，或上传文件..."
                resize="vertical"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                :icon="MagicStick"
                @click="submit"
              >
                开始切分
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="splitResult" class="result-box">
            <div class="result-header">
              <p class="result-label">切分结果：</p>
              <div class="result-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="copyToClipboard(JSON.stringify(splitResult, null, 2))" 
                  text
                >
                  复制JSON
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  :icon="Download"
                  @click="downloadSplitResult"
                  text
                >
                  下载结果
                </el-button>
              </div>
            </div>
            
            <div v-if="splitResult.chunks && splitResult.chunks.length > 0" class="split-result">
              <div class="result-summary">
                <el-tag type="info" size="small">共 {{ splitResult.chunks.length }} 个片段</el-tag>
              </div>
              
              <div class="chunks-list">
                <div v-for="(chunk, index) in splitResult.chunks" :key="index" class="chunk-item">
                  <div class="chunk-header">
                    <span class="chunk-index">片段 {{ index + 1 }}</span>
                    <span class="chunk-length">{{ chunk.length || chunk.text?.length || 0 }} 字符</span>
                    <el-button 
                      size="small" 
                      @click="copyToClipboard(chunk.text || chunk)" 
                      type="text"
                    >
                      复制片段
                    </el-button>
                  </div>
                  <pre class="chunk-content">{{ chunk.text || chunk }}</pre>
                </div>
              </div>
            </div>
            
            <div v-else class="json-result">
              <pre class="result-json">{{ JSON.stringify(splitResult, null, 2) }}</pre>
            </div>
          </div>
        </el-card>

        <!-- 递归字符切分功能 -->
        <el-card class="form-card" shadow="hover" v-if="activeSubFeature === 'split-recursive'">
          <template #header>
            <span>递归字符切分</span>
          </template>
          <el-form label-width="100px" class="text-split-form">
            <el-form-item label="输入方式">
              <div class="input-method-selector">
                <div class="file-upload-area">
                  <input
                    ref="fileInput"
                    type="file"
                    accept=".txt,.md,.markdown,.json"
                    @change="handleFileUpload"
                    style="display: none"
                  />
                  <el-button
                    type="primary"
                    :icon="UploadFilled"
                    @click="fileInput?.click()"
                    size="small"
                  >
                    上传文件
                  </el-button>
                  <span class="file-info" v-if="fileName">
                    {{ fileName }}
                    <el-button
                      type="danger"
                      text
                      size="small"
                      @click="clearFile"
                    >
                      清除
                    </el-button>
                  </span>
                  <span class="file-hint" v-else>
                    支持 txt, md, json 格式，最大 10MB
                  </span>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="或输入文本">
              <el-input
                v-model="form.splitText"
                type="textarea"
                :rows="8"
                placeholder="请输入要切分的文本内容，或上传文件..."
                resize="vertical"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                :icon="MagicStick"
                @click="submit"
              >
                开始切分
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="splitResult" class="result-box">
            <div class="result-header">
              <p class="result-label">切分结果：</p>
              <div class="result-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="copyToClipboard(JSON.stringify(splitResult, null, 2))" 
                  text
                >
                  复制JSON
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  :icon="Download"
                  @click="downloadSplitResult"
                  text
                >
                  下载结果
                </el-button>
              </div>
            </div>
            
            <div v-if="splitResult.chunks && splitResult.chunks.length > 0" class="split-result">
              <div class="result-summary">
                <el-tag type="info" size="small">共 {{ splitResult.chunks.length }} 个片段</el-tag>
              </div>
              
              <div class="chunks-list">
                <div v-for="(chunk, index) in splitResult.chunks" :key="index" class="chunk-item">
                  <div class="chunk-header">
                    <span class="chunk-index">片段 {{ index + 1 }}</span>
                    <span class="chunk-length">{{ chunk.length || chunk.text?.length || 0 }} 字符</span>
                    <el-button 
                      size="small" 
                      @click="copyToClipboard(chunk.text || chunk)" 
                      type="text"
                    >
                      复制片段
                    </el-button>
                  </div>
                  <pre class="chunk-content">{{ chunk.text || chunk }}</pre>
                </div>
              </div>
            </div>
            
            <div v-else class="json-result">
              <pre class="result-json">{{ JSON.stringify(splitResult, null, 2) }}</pre>
            </div>
          </div>
        </el-card>

        <!-- Markdown 切分功能 -->
        <el-card class="form-card" shadow="hover" v-if="activeSubFeature === 'split-markdown'">
          <template #header>
            <span>Markdown 切分</span>
          </template>
          <el-form label-width="100px" class="text-split-form">
            <el-form-item label="输入方式">
              <div class="input-method-selector">
                <div class="file-upload-area">
                  <input
                    ref="fileInput"
                    type="file"
                    accept=".txt,.md,.markdown,.json"
                    @change="handleFileUpload"
                    style="display: none"
                  />
                  <el-button
                    type="primary"
                    :icon="UploadFilled"
                    @click="fileInput?.click()"
                    size="small"
                  >
                    上传文件
                  </el-button>
                  <span class="file-info" v-if="fileName">
                    {{ fileName }}
                    <el-button
                      type="danger"
                      text
                      size="small"
                      @click="clearFile"
                    >
                      清除
                    </el-button>
                  </span>
                  <span class="file-hint" v-else>
                    支持 txt, md, json 格式，最大 10MB
                  </span>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="或输入文本">
              <el-input
                v-model="form.splitText"
                type="textarea"
                :rows="8"
                placeholder="请输入要切分的文本内容，或上传文件..."
                resize="vertical"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                :icon="MagicStick"
                @click="submit"
              >
                开始切分
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="splitResult" class="result-box">
            <div class="result-header">
              <p class="result-label">切分结果：</p>
              <div class="result-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="copyToClipboard(JSON.stringify(splitResult, null, 2))" 
                  text
                >
                  复制JSON
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  :icon="Download"
                  @click="downloadSplitResult"
                  text
                >
                  下载结果
                </el-button>
              </div>
            </div>
            
            <div v-if="splitResult.chunks && splitResult.chunks.length > 0" class="split-result">
              <div class="result-summary">
                <el-tag type="info" size="small">共 {{ splitResult.chunks.length }} 个片段</el-tag>
              </div>
              
              <div class="chunks-list">
                <div v-for="(chunk, index) in splitResult.chunks" :key="index" class="chunk-item">
                  <div class="chunk-header">
                    <span class="chunk-index">片段 {{ index + 1 }}</span>
                    <span class="chunk-length">{{ chunk.length || chunk.text?.length || 0 }} 字符</span>
                    <el-button 
                      size="small" 
                      @click="copyToClipboard(chunk.text || chunk)" 
                      type="text"
                    >
                      复制片段
                    </el-button>
                  </div>
                  <pre class="chunk-content">{{ chunk.text || chunk }}</pre>
                </div>
              </div>
            </div>
            
            <div v-else class="json-result">
              <pre class="result-json">{{ JSON.stringify(splitResult, null, 2) }}</pre>
            </div>
          </div>
        </el-card>

        <!-- Python 切分功能 -->
        <el-card class="form-card" shadow="hover" v-if="activeSubFeature === 'split-python'">
          <template #header>
            <span>Python 切分</span>
          </template>
          <el-form label-width="100px" class="text-split-form">
            <el-form-item label="输入方式">
              <div class="input-method-selector">
                <div class="file-upload-area">
                  <input
                    ref="fileInput"
                    type="file"
                    accept=".txt,.md,.markdown,.json,.py"
                    @change="handleFileUpload"
                    style="display: none"
                  />
                  <el-button
                    type="primary"
                    :icon="UploadFilled"
                    @click="fileInput?.click()"
                    size="small"
                  >
                    上传文件
                  </el-button>
                  <span class="file-info" v-if="fileName">
                    {{ fileName }}
                    <el-button
                      type="danger"
                      text
                      size="small"
                      @click="clearFile"
                    >
                      清除
                    </el-button>
                  </span>
                  <span class="file-hint" v-else>
                    支持 txt, md, json, py 格式，最大 10MB
                  </span>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="或输入文本">
              <el-input
                v-model="form.splitText"
                type="textarea"
                :rows="8"
                placeholder="请输入要切分的文本内容，或上传文件..."
                resize="vertical"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                :icon="MagicStick"
                @click="submit"
              >
                开始切分
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="splitResult" class="result-box">
            <div class="result-header">
              <p class="result-label">切分结果：</p>
              <div class="result-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="copyToClipboard(JSON.stringify(splitResult, null, 2))" 
                  text
                >
                  复制JSON
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  :icon="Download"
                  @click="downloadSplitResult"
                  text
                >
                  下载结果
                </el-button>
              </div>
            </div>
            
            <div v-if="splitResult.chunks && splitResult.chunks.length > 0" class="split-result">
              <div class="result-summary">
                <el-tag type="info" size="small">共 {{ splitResult.chunks.length }} 个片段</el-tag>
              </div>
              
              <div class="chunks-list">
                <div v-for="(chunk, index) in splitResult.chunks" :key="index" class="chunk-item">
                  <div class="chunk-header">
                    <span class="chunk-index">片段 {{ index + 1 }}</span>
                    <span class="chunk-length">{{ chunk.length || chunk.text?.length || 0 }} 字符</span>
                    <el-button 
                      size="small" 
                      @click="copyToClipboard(chunk.text || chunk)" 
                      type="text"
                    >
                      复制片段
                    </el-button>
                  </div>
                  <pre class="chunk-content">{{ chunk.text || chunk }}</pre>
                </div>
              </div>
            </div>
            
            <div v-else class="json-result">
              <pre class="result-json">{{ JSON.stringify(splitResult, null, 2) }}</pre>
            </div>
          </div>
        </el-card>

      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.text-split-view {
  min-height: calc(100vh - var(--nav-height));
  padding: 40px var(--padding-inline) 80px;
  position: relative;
  overflow: hidden;
}

.text-split-bg-deco {
  pointer-events: none;
  position: absolute;
  inset: 0;
}
.text-split-bg-deco .circle {
  position: absolute;
  border-radius: 50%;
  background: var(--primary-gradient);
  opacity: 0.06;
  animation: float 5s ease-in-out infinite;
}
.text-split-bg-deco .circle-1 {
  width: 200px;
  height: 200px;
  top: 15%;
  right: 8%;
}
.text-split-bg-deco .circle-2 {
  width: 140px;
  height: 140px;
  bottom: 25%;
  left: 8%;
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.text-split-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  max-width: var(--content-max-width);
  margin: 0 auto 24px;
  padding: 0 0 24px;
  border-bottom: 1px solid var(--gray-200);
}
.text-split-header .header-right {
  text-align: left;
  flex: 1;
}

/* 新增信息卡片样式 */
.info-card {
  margin: 16px 16px 16px 16px;
  border: 1px solid #007bff;
  padding: 8px 8px 8px 8px;
  border-radius: 6px;
}
.info-card .el-card__header,
.info-card :deep(.el-card__header) {
  color: #44aff6 !important;
  font-weight: 600;
  font-size: 18px;
  margin-top: -10px;
  margin-bottom: -26px;
}
.info-content {
  font-size: 14px;
  margin-top: 0px;
  margin-bottom: -20px;
  color: var(--gray-700);
}
.info-content .section {
  margin-bottom: 10px;
}
.info-content h4 {
  margin: 0 0 4px;
  font-size: 15px;
  color: var(--gray-900);
  font-weight: 600;
}
.info-content ul,
.info-content ol {
  margin: 4px 0 0 20px;
}
.info-content li {
  margin: 2px 0;
}

.text-split-inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  position: relative;
  z-index: 1;
}
.text-split-content {
  width: 100%;
}

.selector-card {
  margin-bottom: 16px;
  border-radius: 10px;
}

.selector-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selector-label {
  font-size: 14px;
  color: var(--gray-700);
  font-weight: 500;
}

.method-select {
  width: 240px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 2px;
  color: var(--gray-900);
}
.page-desc {
  font-size: 15px;
  color: var(--gray-600);
  margin-bottom: 4px;
}

.health-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.health-label {
  font-size: 14px;
  color: var(--gray-600);
}

.form-card {
  border-radius: var(--card-radius-lg);
  margin-bottom: 24px;
  :deep(.el-card__header) {
    font-weight: 600;
    color: var(--gray-900);
  }
}

.text-split-form {
  max-width: 720px;
  
  .input-method-selector {
    width: 100%;
    
    .file-upload-area {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 12px;
      border: 1px dashed var(--gray-300);
      border-radius: 4px;
      background: var(--gray-50);
      
      .file-info {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        background: white;
        border-radius: 4px;
        border: 1px solid var(--gray-200);
        font-size: 13px;
        color: var(--gray-700);
      }
      
      .file-hint {
        font-size: 12px;
        color: var(--gray-500);
        text-align: center;
      }
    }
  }
}

.result-box {
  margin-top: 20px;
  padding: 20px;
  background: var(--gray-50);
  border-radius: 8px;
  border: 1px solid var(--gray-200);
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  .result-label {
    font-weight: 600;
    margin: 0;
    color: var(--gray-800);
    font-size: 15px;
  }
  
  .result-actions {
    display: flex;
    gap: 8px;
  }
}
.result-json {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  overflow: auto;
  max-height: 400px;
  padding: 12px;
  background: var(--gray-100);
  border-radius: 6px;
  border: 1px solid var(--gray-300);
}
.result-json {
  color: var(--gray-700);
}

// 切片结果样式
.split-result {
  .result-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--gray-200);
    
    .download-btn {
      margin-left: auto;
    }
  }
  .chunks-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .chunk-item {
    background: white;
    border-radius: 6px;
    border: 1px solid var(--gray-200);
    overflow: hidden;
  }
  .chunk-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--gray-50);
    border-bottom: 1px solid var(--gray-200);
  }
  .chunk-index {
    font-weight: 500;
    color: var(--gray-800);
    font-size: 13px;
  }
  .chunk-length {
    color: var(--gray-600);
    font-size: 12px;
  }
  .chunk-content {
    margin: 0;
    padding: 12px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 200px;
    overflow: auto;
    background: var(--gray-50);
  }
}

@media (max-width: 768px) {
  .text-split-view {
    padding: 24px 20px 60px;
  }
  .page-title {
    font-size: 22px;
  }
  .page-desc {
    font-size: 14px;
  }
  .chunk-header {
    flex-wrap: wrap;
    gap: 8px;
  }
  .selector-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .method-select {
    width: 100%;
  }
  
  .text-split-form {
    .input-method-selector {
      .file-upload-area {
        .file-info {
          flex-direction: column;
          align-items: flex-start;
          gap: 4px;
        }
      }
    }
  }
}

.results-list {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.result-item {
  margin-bottom: 20px;
}
</style>
