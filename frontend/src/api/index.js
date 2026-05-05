import { request } from './request'
/**
 * 前端 API 统一导出
 * 按模块划分：智能问答、知识管理、组件管理
 * 使用方式：import { sendChatMessage, knowledgeQuery, knowledgeExtract } from '@/api'
 */

// 认证与用户管理
export {
  loginApi,
  registerApi,
  getMeApi,
  listUsersApi,
  createUserApi,
  updateUserApi,
  deleteUserApi
} from './modules/auth'

// 智能问答
export { sendChatMessage } from './modules/chat'

// 知识管理：文档管理、检索
export {
  getDocuments,
  checkDocumentNameExists,
  uploadDocument,
  deleteDocument,
  downloadDocument,
  knowledgeQuery
} from './modules/knowledge'

// 组件管理：知识抽取、知识图谱更新、文本切分等
export { knowledgeExtract, extractHealthCheck, storeGraphToNeo4j, parseChunkedJsonExtract } from './modules/component'
export {
  kgUpdateHealthCheck,
  kgUpdateAdd,
  kgUpdateDelete,
  kgUpdateStatistics,
  kgCalculateConfidence,
  processSchemaOutput,   
  addFromComputed        
} from './modules/component/kg-update'
export { textSplitHealthCheck } from './modules/component'
export {
  intentRecognitionHealthCheck,
  intentRecognitionRecognize,
  intentRecognitionDeepRecognize,
  intentRecognitionGetPlan,
  intentRecognitionGetTools
} from './modules/component'
export { answerGenerationHealthCheck, answerGenerationAsk, answerGenerationAskVisualize, answerGenerationQueryGraph } from './modules/component'
export { documentPreprocHealthCheck, documentPreprocConvert, documentPreprocConvertToPdf, getAvailableModels } from './modules/component'
// -----------------------------------------------------------------------------
// 文本切片接口
// -----------------------------------------------------------------------------

/**
 * 切片：递归字符
 * @param {string} text
 */
export function textSplitCharacter(text) {
  return request.post('/component/text-split/split/character',
    { text: text },
    { timeout: 120000 }
  )
}

/**
 * 切片：递归字符
 * @param {string} text
 */
export function textSplitRecursive(text) {
  return request.post('/component/text-split/split/recursive', { text: text }, { timeout: 120000 })
}

/**
 * 切片：Markdown
 * @param {string} text
 */
export function textSplitMarkdown(text, requestConfig = {}) {
  return request.post('/component/text-split/split/markdown', { text: text }, { timeout: 120000, ...requestConfig })
}

/**
 * 切片：Python 代码
 * @param {string} text
 */
export function textSplitPython(text) {
  return request.post('/component/text-split/split/python', { text: text }, { timeout: 120000 })
}

export const mutiRetriever = () => {
  return request({
    url: '/component/text-split/mutiRetriever',
    method: 'get'
  })
}

