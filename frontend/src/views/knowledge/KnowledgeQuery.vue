<script setup></script>

<template>
  <div class="knowledge-query">
    <div class="database-stack">
      <el-card class="panel-card database-card" shadow="hover">
        <template #header>
          <span class="panel-title">向量数据库</span>
          <el-tag type="info" size="small" class="panel-tag">Milvus</el-tag>
        </template>
        <div class="db-section">
          <h4 class="section-title">向量数据库管理</h4>
          <div class="link-actions">
            <a
              class="link-pill link-pill--success"
              href="http://localhost:8787/#/databases/default/collections"
              target="_blank"
              rel="noopener noreferrer"
            >
              向量数据库管理
            </a>
          </div>
          <div class="tips-box">
            <div class="tip-item">- 集合：default / collections</div>
            <div class="tip-item">- 可查看向量集合、分片与数据分布</div>
            <div class="tip-item">- 建议按业务域维护集合和分区</div>
          </div>
        </div>
      </el-card>

      <el-card class="panel-card database-card" shadow="hover">
        <template #header>
          <span class="panel-title">图数据库</span>
          <el-tag type="warning" size="small" class="panel-tag">Neo4j</el-tag>
        </template>
        <div class="db-section">
          <h4 class="section-title">图数据库管理</h4>
          <div class="link-actions">
            <a
              class="link-pill link-pill--primary"
              href="http://localhost:7474/browser/"
              target="_blank"
              rel="noopener noreferrer"
            >
              图数据库管理
            </a>
          </div>
          <div class="tips-box">
            <div class="tip-item">- 实体节点：术语、规则类型、系统要素</div>
            <div class="tip-item">- 关系边：定义、从属、关联、约束</div>
            <div class="tip-item">- 建议在管理台中结合 Cypher 做结构化验证</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped lang="scss">
.knowledge-query {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

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

.database-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.database-card {
  width: 100%;
}

.db-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-800);
}

.link-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-start;
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

.tips-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  padding: 12px 14px;
}

.tip-item {
  font-size: 13px;
  color: var(--gray-700);
  line-height: 1.7;
}
</style>
