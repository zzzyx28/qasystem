/**
 * 组件管理 - 文本切分 API
 * 请求主站后端 /api/component/text-split
 */
import { request } from '../../request'

/** 健康检查：GET /api/component/text-split/health */
export function textSplitHealthCheck() {
  return request.get('/component/text-split/health', { timeout: 5000 })
}
