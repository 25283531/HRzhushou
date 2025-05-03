<template>
  <div class="data-analysis-container">
    <h1>数据分析</h1>
    
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>数据分析</span>
          <el-button type="primary" @click="generateReport">生成报表</el-button>
        </div>
      </template>
      
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="form-inline">
          <el-form-item label="分析类型">
            <el-select v-model="filterForm.analysisType" placeholder="选择分析类型">
              <el-option label="考勤分析" value="attendance" />
              <el-option label="薪资分析" value="salary" />
              <el-option label="人员结构分析" value="employee" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="部门">
            <el-select v-model="filterForm.department" placeholder="选择部门" clearable>
              <el-option
                v-for="item in departments"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadAnalysisData">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 数据分析图表区域 -->
      <div v-loading="loading" class="chart-container">
        <!-- 考勤分析图表 -->
        <div v-if="filterForm.analysisType === 'attendance'" class="chart-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-card">
                <h3>考勤出勤率</h3>
                <div class="chart-placeholder" ref="attendanceRateChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-card">
                <h3>迟到/早退统计</h3>
                <div class="chart-placeholder" ref="lateEarlyChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <div class="chart-card">
                <h3>考勤异常趋势</h3>
                <div class="chart-placeholder" ref="attendanceTrendChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 薪资分析图表 -->
        <div v-if="filterForm.analysisType === 'salary'" class="chart-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-card">
                <h3>部门薪资分布</h3>
                <div class="chart-placeholder" ref="salaryDistributionChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-card">
                <h3>薪资组成分析</h3>
                <div class="chart-placeholder" ref="salaryComponentChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <div class="chart-card">
                <h3>薪资趋势</h3>
                <div class="chart-placeholder" ref="salaryTrendChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 人员结构分析图表 -->
        <div v-if="filterForm.analysisType === 'employee'" class="chart-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-card">
                <h3>部门人员分布</h3>
                <div class="chart-placeholder" ref="departmentDistributionChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-card">
                <h3>员工年龄分布</h3>
                <div class="chart-placeholder" ref="ageDistributionChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="24">
              <div class="chart-card">
                <h3>员工入职/离职趋势</h3>
                <div class="chart-placeholder" ref="employeeTrendChart">
                  <div class="empty-chart-message" v-if="!hasData">
                    <el-icon><DataLine /></el-icon>
                    <span>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      
      <!-- 数据表格 -->
      <div class="table-container" v-if="hasData">
        <h3>详细数据</h3>
        <el-table
          :data="tableData"
          border
          style="width: 100%"
          max-height="400"
        >
          <el-table-column v-for="column in tableColumns" :key="column.prop" :prop="column.prop" :label="column.label" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { DataLine } from '@element-plus/icons-vue'
import { validateExcelFile } from '../../utils/dataValidator'

// 数据加载状态
const loading = ref(false)
const hasData = ref(false)

// 部门列表
const departments = ref([])

// 筛选表单
const filterForm = reactive({
  analysisType: 'attendance', // 默认考勤分析
  dateRange: [
    new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    new Date().toISOString().split('T')[0]
  ], // 默认当月，格式化为 YYYY-MM-DD
  department: ''
})

// 图表实例引用
const chartInstances = reactive({});

// 图表DOM引用
const attendanceRateChart = ref(null)
const lateEarlyChart = ref(null)
const attendanceTrendChart = ref(null)
const salaryDistributionChart = ref(null)
const salaryComponentChart = ref(null)
const salaryTrendChart = ref(null)
const departmentDistributionChart = ref(null)
const ageDistributionChart = ref(null)
const employeeTrendChart = ref(null)

// 表格数据
const tableData = ref([])
const tableColumns = ref([])

// 初始化数据
onMounted(() => {
  loadDepartments()
  loadAnalysisData()
})

// 监听分析类型变化，重新加载数据
watch(() => filterForm.analysisType, () => {
  loadAnalysisData()
})

// 加载部门数据
const loadDepartments = async () => {
  try {
    // 导入API模块
    const { default: api } = await import('../../api')
    
    // 调用API获取部门数据
    const response = await api.get('/departments')
    
    if (response.success) {
      departments.value = response.data || []
    } else {
      ElMessage.error(response.error || '加载部门失败')
      departments.value = []
    }
  } catch (error) {
    console.error('加载部门失败:', error)
    ElMessage.error('加载部门失败')
  }
}

// 加载分析数据
const loadAnalysisData = async () => {
  loading.value = true
  hasData.value = false
  tableData.value = []
  tableColumns.value = []
  // 清理旧的图表实例
  Object.values(chartInstances).forEach(chart => chart?.dispose());

  try {
    const { default: api } = await import('../../api')
    const params = {
      type: filterForm.analysisType,
      startDate: filterForm.dateRange ? filterForm.dateRange[0] : null,
      endDate: filterForm.dateRange ? filterForm.dateRange[1] : null,
      departmentId: filterForm.department || null
    }
    const response = await api.get('/analysis', { params })

    if (response.success && response.data) {
      const analysisData = response.data;
      tableData.value = analysisData.tableData || [];
      tableColumns.value = analysisData.tableColumns || [];
      hasData.value = tableData.value.length > 0 || Object.keys(analysisData.chartData || {}).length > 0;
      
      if (hasData.value) {
         // 等待DOM更新后再初始化图表
        nextTick(() => {
          initCharts(analysisData.chartData)
        });
      }
    } else {
      ElMessage.error(response.error || '加载分析数据失败')
      hasData.value = false;
    }
  } catch (error) {
    console.error('加载分析数据失败:', error)
    ElMessage.error('加载分析数据失败')
    hasData.value = false;
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initCharts = (chartData) => {
  if (!chartData) return;

  const initSingleChart = (refName, chartRef, options) => {
    if (chartRef.value && options) {
      let chart = chartInstances[refName];
      if (!chart) {
         chart = echarts.init(chartRef.value);
         chartInstances[refName] = chart;
      }
      chart.setOption(options);
      // 添加窗口大小调整监听
      window.addEventListener('resize', () => chart.resize());
    } else {
       console.warn(`Chart element or options not available for ${refName}`);
    }
  }

  // 根据不同的分析类型初始化不同的图表
  if (filterForm.analysisType === 'attendance' && chartData.attendance) {
    initSingleChart('attendanceRateChart', attendanceRateChart, chartData.attendance.rateOption);
    initSingleChart('lateEarlyChart', lateEarlyChart, chartData.attendance.lateEarlyOption);
    initSingleChart('attendanceTrendChart', attendanceTrendChart, chartData.attendance.trendOption);
  } else if (filterForm.analysisType === 'salary' && chartData.salary) {
    initSingleChart('salaryDistributionChart', salaryDistributionChart, chartData.salary.distributionOption);
    initSingleChart('salaryComponentChart', salaryComponentChart, chartData.salary.componentOption);
    initSingleChart('salaryTrendChart', salaryTrendChart, chartData.salary.trendOption);
  } else if (filterForm.analysisType === 'employee' && chartData.employee) {
    initSingleChart('departmentDistributionChart', departmentDistributionChart, chartData.employee.departmentOption);
    initSingleChart('ageDistributionChart', ageDistributionChart, chartData.employee.ageOption);
    initSingleChart('employeeTrendChart', employeeTrendChart, chartData.employee.trendOption);
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.dateRange = [
    new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    new Date().toISOString().split('T')[0]
  ]
  filterForm.department = ''
  loadAnalysisData()
}

// 生成报表
const generateReport = async () => {
  try {
    loading.value = true
    const { default: api } = await import('../../api')
    const params = {
      type: filterForm.analysisType,
      startDate: filterForm.dateRange ? filterForm.dateRange[0] : null,
      endDate: filterForm.dateRange ? filterForm.dateRange[1] : null,
      departmentId: filterForm.department || null,
      format: 'excel' // 请求Excel格式
    }
    const response = await api.get('/analysis/report', { params, responseType: 'blob' })

    if (response) { // blob响应通常没有success字段，直接检查响应体
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      const fileName = `数据分析报表_${filterForm.analysisType}_${new Date().toLocaleDateString()}.xlsx`;
      link.download = fileName;
      link.click();
      window.URL.revokeObjectURL(link.href);
      ElMessage.success('报表生成成功')
    } else {
      ElMessage.error('生成报表失败')
    }
  } catch (error) {
    console.error('生成报表失败:', error)
    ElMessage.error('生成报表失败')
  } finally {
    loading.value = false
  }
}

// 组件卸载时清理图表实例和事件监听
onUnmounted(() => {
  Object.values(chartInstances).forEach(chart => {
    if (chart) {
      window.removeEventListener('resize', () => chart.resize());
      chart.dispose();
    }
  });
});
</script>

<style scoped>
.data-analysis-container {
  padding: 20px;
}

.main-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  margin-bottom: 20px;
}

.form-inline .el-form-item {
  margin-right: 15px;
  margin-bottom: 10px; /* 增加底部间距 */
}

.chart-container {
  min-height: 300px; /* 保证加载时有高度 */
}

.chart-section {
  margin-bottom: 30px;
}

.chart-card {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.chart-placeholder {
  height: 300px; /* 固定图表高度 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9; /* 浅灰色背景 */
}

.empty-chart-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #909399;
}

.empty-chart-message .el-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.table-container {
  margin-top: 30px;
}

.table-container h3 {
  margin-bottom: 15px;
  font-size: 16px;
}
</style>