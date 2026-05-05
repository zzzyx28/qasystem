/**
 * 组件管理 - API 统一入口
 * 新增组件时：在此导出对应模块的接口
 */
export { knowledgeExtract, extractHealthCheck, storeGraphToNeo4j, parseChunkedJsonExtract } from './knowledge-extract'
export { 
  kgUpdateHealthCheck, 
  kgUpdateAdd, 
  kgUpdateDelete, 
  kgUpdateStatistics, 
  kgCalculateConfidence,
  processSchemaOutput,   
  addFromComputed        
} from './kg-update'
export { textSplitHealthCheck } from './text-split'
export {
  intentRecognitionHealthCheck,
  intentRecognitionRecognize,
  intentRecognitionDeepRecognize,
  intentRecognitionGetPlan,
  intentRecognitionGetTools
} from './intent-recognition'
export { answerGenerationHealthCheck, answerGenerationAsk, answerGenerationAskVisualize, answerGenerationQueryGraph } from './answer-generation'
export { documentPreprocHealthCheck, documentPreprocConvert, documentPreprocConvertToPdf, getAvailableModels } from './document-preproc'
