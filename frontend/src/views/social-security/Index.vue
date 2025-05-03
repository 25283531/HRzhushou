<template>
  <div class="social-security-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>社保管理</h2>
          <div class="header-actions">
            <el-button type="primary">
              <el-icon><Plus /></el-icon> 添加社保组
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 社保组列表 -->
      <el-table
        :data="socialSecurityGroups"
        border
        style="width: 100%">
        <el-table-column prop="name" label="社保组名称" width="180" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="employee_count" label="员工数量" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary">查看详情</el-button>
            <el-button size="small" type="warning">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 社保组数据
const socialSecurityGroups = ref([
  {
    id: 1,
    name: '标准社保组',
    description: '适用于普通员工的标准社保缴纳方案',
    employee_count: 24
  },
  {
    id: 2,
    name: '高级社保组',
    description: '适用于管理层的高级社保缴纳方案',
    employee_count: 8
  }
])

</script>

<style scoped>
.social-security-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>