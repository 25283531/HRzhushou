<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="welcome-section">
          <h1>欢迎使用 HR助手</h1>
          <p>一站式薪酬管理解决方案，助力企业高效管理人力资源</p>
        </div>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>员工总数</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">0</div>
            <div class="stat-text">名员工</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <el-icon><Money /></el-icon>
              <span>薪资组</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">0</div>
            <div class="stat-text">个薪资组</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <el-icon><Service /></el-icon>
              <span>社保组</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">0</div>
            <div class="stat-text">个社保组</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <el-icon><Calendar /></el-icon>
              <span>考勤记录</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">0</div>
            <div class="stat-text">条记录</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="quick-access">
      <el-col :span="24">
        <h2>快速操作</h2>
      </el-col>
      <el-col :xs="24" :sm="8" v-for="(item, index) in quickAccessItems" :key="index">
        <el-card shadow="hover" class="quick-card" @click="navigateTo(item.path)">
          <div class="quick-card-content">
            <el-icon :size="32"><component :is="item.icon" /></el-icon>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Money, Service, Calendar, Upload, Document, DataAnalysis } from '@element-plus/icons-vue'

const router = useRouter()

// 快速操作项
const quickAccessItems = ref([
  {
    title: '导入考勤数据',
    description: '从Excel文件导入员工考勤数据',
    icon: 'Upload',
    path: '/attendance'
  },
  {
    title: '员工管理',
    description: '添加、编辑和管理员工信息',
    icon: 'User',
    path: '/employee'
  },
  {
    title: '薪资计算',
    description: '计算员工薪资并生成薪资报表',
    icon: 'Document',
    path: '/salary-calculation'
  },
  {
    title: '薪资组管理',
    description: '创建和管理薪资组及薪酬项',
    icon: 'Money',
    path: '/salary-group'
  },
  {
    title: '社保管理',
    description: '设置社保项目和社保组',
    icon: 'Service',
    path: '/social-security'
  },
  {
    title: '数据分析',
    description: '查看人工成本和薪酬占比分析',
    icon: 'DataAnalysis',
    path: '/data-analysis'
  }
])

// 导航到指定路径
const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #409EFF 0%, #36D1DC 100%);
  color: white;
  border-radius: 8px;
}

.welcome-section h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 16px;
  opacity: 0.9;
}

.stat-cards {
  margin-bottom: 30px;
}

.stat-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.card-header .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.card-content {
  text-align: center;
  padding: 10px 0;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.stat-text {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.quick-access h2 {
  margin-bottom: 20px;
  font-size: 20px;
  color: #303133;
}

.quick-card {
  height: 180px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.quick-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 20px;
}

.quick-card-content .el-icon {
  margin-bottom: 15px;
  color: #409EFF;
}

.quick-card-content h3 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #303133;
}

.quick-card-content p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}
</style>