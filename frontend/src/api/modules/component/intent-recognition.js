/**
 * 组件管理 - 意图识别 API
 * 请求主站后端 /api/component/intent-recognition
 */
import { request } from '../../request'

/** 健康检查：GET /api/component/intent-recognition/health */
export function intentRecognitionHealthCheck() {
  return request.get('/component/intent-recognition/health', { timeout: 5000 })
}

/**
 * 意图识别
 * @param {object} params - { text }
 */
export function intentRecognitionRecognize(params) {
  return request.post('/component/intent-recognition/recognize', {
    text: params.text
  }, { timeout: 6000 })
}

/**
 * 深度意图识别
 * @param {object} params - { text }
 */
export function intentRecognitionDeepRecognize(params) {
  return request.post('/component/intent-recognition/deep-recognize', {
    text: params.text
  }, { timeout: 10000 })
}

/**
 * 获取计划
 * @param {object} params - { intent_name, domain_name }
 */
export function intentRecognitionGetPlan(params) {
  return request.post('/component/intent-recognition/get-plan', {
    intent_name: params.intent_name,
    domain_name: params.domain_name
  }, { timeout: 10000 })
}

/**
 * 获取工具
 * @param {object} params - { intent_name, domain_name }
 */
export function intentRecognitionGetTools(params = {}) {
  return request.post('/component/intent-recognition/get-tools', {
    intent_name: params.intent_name || '',
    domain_name: params.domain_name || ''
  }, { timeout: 10000 })
}
