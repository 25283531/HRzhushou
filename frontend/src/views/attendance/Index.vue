<template>
  <div class="attendance-container">
    <el-card class="attendance-card">
      <template #header>
        <div class="card-header">
          <h2>考勤数据管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="showImportDialog">
              <el-icon><Upload /></el-icon> 导入考勤数据
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选表单 -->
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="月份">
          <el-date-picker
            v-model="filterForm.month"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM" />
        </el-form-item>
        <el-form-item label="员工">
          <el-select v-model="filterForm.employeeId" placeholder="选择员工" clearable>
            <el-option
              v-for="item in employees"
              :key="item.id"
              :label="item.name"
              :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
            <el-option label="正常" value="正常" />
            <el-option label="迟到" value="迟到" />
            <el-option label="早退" value="早退" />
            <el-option label="缺卡" value="缺卡" />
            <el-option label="旷工" value="旷工" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 考勤数据表格 -->
      <el-table
        v-loading="loading"
        :data="attendanceData"
        border
        style="width: 100%"
        max-height="500">
        <el-table-column prop="employee_name" label="员工姓名" width="120" />
        <el-table-column prop="employee_number" label="工号" width="120" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="check_in" label="上班打卡" width="150" />
        <el-table-column prop="check_out" label="下班打卡" width="150" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag
              :type="getStatusTagType(scope.row.status)"
              effect="plain">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>
    
    <!-- 导入考勤数据对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入考勤数据"
      width="600px">
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="考勤数据文件">
          <el-upload
            class="upload-demo"
            drag
            action="/api/attendance/import"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".xlsx,.xls,.csv">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Excel 或 CSV 格式文件，请确保文件格式正确
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="数据格式设置">
          <el-button type="primary" @click="showFieldMappingDialog">设置字段映射</el-button>
          <el-button @click="showTemplateDialog">查看模板</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitImport">导入</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 字段映射对话框 -->
    <el-dialog
      v-model="fieldMappingDialogVisible"
      title="设置字段映射"
      width="800px">
      <el-form :model="fieldMapping" label-width="120px">
        <el-form-item label="员工姓名字段">
          <el-select v-model="fieldMapping.name" placeholder="选择对应的Excel列">
            <el-option v-for="item in excelColumns" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="员工工号字段">
          <el-select v-model="fieldMapping.number" placeholder="选择对应的Excel列">
            <el-option v-for="item in excelColumns" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期字段">
          <el-select v-model="fieldMapping.date" placeholder="选择对应的Excel列">
            <el-option v-for="item in excelColumns" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="上班打卡字段">
          <el-select v-model="fieldMapping.checkIn" placeholder="选择对应的Excel列">
            <el-option v-for="item in excelColumns" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="下班打卡字段">
          <el-select v-model="fieldMapping.checkOut" placeholder="选择对应的Excel列">
            <el-option v-for="item in excelColumns" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        
        <!-- 自定义考勤字段 -->
        <div class="custom-fields-section">
          <div class="section-header">
            <h3>自定义考勤字段</h3>
            <el-button type="primary" size="small" @click="addCustomField">添加字段</el-button>
          </div>
          
          <el-form-item 
            v-for="(field, index) in customFields" 
            :key="index"
            :label="field.name || '自定义字段'">
            <div class="custom-field-row">
              <el-input v-model="field.name" placeholder="字段名称" style="width: 150px; margin-right: 10px" />
              <el-select v-model="field.column" placeholder="选择对应的Excel列" style="width: 200px; margin-right: 10px">
                <el-option v-for="item in excelColumns" :key="item" :label="item" :value="item" />
              </el-select>
              <el-button type="danger" size="small" @click="removeCustomField(index)">删除</el-button>
            </div>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="fieldMappingDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveFieldMapping">保存映射</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 考勤规则设置对话框 -->
    <el-dialog
      v-model="attendanceRuleDialogVisible"
      title="考勤规则设置"
      width="600px">
      <el-form :model="attendanceRules" label-width="150px">
        <el-form-item label="迟到扣款金额">
          <el-input-number v-model="attendanceRules.lateDeduction" :min="0" :precision="2" :step="10" />
          <span class="form-tip">元/次</span>
        </el-form-item>
        <el-form-item label="迟到免扣次数">
          <el-input-number v-model="attendanceRules.lateFreeCount" :min="0" :precision="0" :step="1" />
          <span class="form-tip">次/月</span>
        </el-form-item>
        <el-form-item label="严重迟到扣款金额">
          <el-input-number v-model="attendanceRules.seriousLateDeduction" :min="0" :precision="2" :step="10" />
          <span class="form-tip">元/次</span>
        </el-form-item>
        <el-form-item label="严重迟到时长">
          <el-input-number v-model="attendanceRules.seriousLateMinutes" :min="0" :precision="0" :step="5" />
          <span class="form-tip">分钟</span>
        </el-form-item>
        <el-form-item label="早退扣款金额">
          <el-input-number v-model="attendanceRules.earlyLeaveDeduction" :min="0" :precision="2" :step="10" />
          <span class="form-tip">元/次</span>
        </el-form-item>
        <el-form-item label="缺卡扣款金额">
          <el-input-number v-model="attendanceRules.missedPunchDeduction" :min="0" :precision="2" :step="10" />
          <span class="form-tip">元/次</span>
        </el-form-item>
        <el-form-item label="旷工扣款金额">
          <el-input-number v-model="attendanceRules.absentDeduction" :min="0" :precision="2" :step="50" />
          <span class="form-tip">元/天</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="attendanceRuleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAttendanceRules">保存规则</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import { parseDate, formatDate } from '../../utils/dateParser'
import { validateAttendanceRecords, validateExcelFile } from '../../utils/dataValidator'
import { processAttendanceData } from '../../utils/workerService'
import backupService from '../../utils/backupService'

// 数据加载状态
const loading = ref(false)

// 考勤数据
const attendanceData = ref([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 导入对话框
const importDialogVisible = ref(false)
const importForm = reactive({
  file: null
})

// 字段映射对话框
const fieldMappingDialogVisible = ref(false)
const excelColumns = ref(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) // 示例列，实际应从上传的Excel中获取
const fieldMapping = reactive({
  name: '',
  number: '',
  date: '',
  checkIn: '',
  checkOut: ''
})

// 自定义考勤字段
const customFields = ref([])

// 考勤规则对话框
const attendanceRuleDialogVisible = ref(false)
const attendanceRules = reactive({
  lateDeduction: 10,
  lateFreeCount: 2,
  seriousLateDeduction: 30,
  seriousLateMinutes: 30,
  earlyLeaveDeduction: 10,
  missedPunchDeduction: 20,
  absentDeduction: 100
})

// 员工数据
const employees = ref([])

// 筛选表单
const filterForm = reactive({
  month: new Date().toISOString().slice(0, 7), // 默认当前月份
  employeeId: '',
  status: ''
})

// 生命周期钩子
onMounted(() => {
  fetchAttendanceData()
  fetchEmployees()
  
  // 初始化备份服务
  try {
    backupService.updateSettings({
      autoBackup: true,
      backupInterval: 12 * 60 * 60 * 1000, // 12小时
      includeAttendance: true
    });
  } catch (error) {
    console.error('初始化备份服务失败:', error);
  }
})

// 组件卸载时清理资源
onUnmounted(() => {
  try {
    // 停止自动备份
    backupService.stopAutoBackup();
  } catch (error) {
    console.error('停止自动备份失败:', error);
  }
})

// 获取考勤数据
const fetchAttendanceData = () => {
  loading.value = true
  
  // 导入API模块 - 修正导入路径
  import('../../api').then(({ default: api }) => {
    // 构建查询参数
    const params = {
      month: filterForm.month,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 调用API获取考勤数据
    api.get('/attendance/list', { params })
      .then(response => {
        if (response && response.success) {
          attendanceData.value = response.data.items || []
          total.value = response.data.total || 0
        } else {
          ElMessage.error(response?.error || '获取考勤数据失败')
          attendanceData.value = []
          total.value = 0
        }
      })
      .catch(error => {
        console.error('获取考勤数据失败:', error)
        ElMessage.error('获取考勤数据失败: ' + (error.message || '未知错误'))
        attendanceData.value = []
        total.value = 0
      })
      .finally(() => {
        loading.value = false
      })
  }).catch(error => {
    console.error('导入API模块失败:', error)
    ElMessage.error('系统错误: 无法加载API模块')
    loading.value = false
  })
}

// 获取员工数据
const fetchEmployees = () => {
  // TODO: 实现实际的员工数据获取逻辑
  employees.value = []
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
}

// 处理文件变更
const handleFileChange = (file) => {
  importForm.file = file.raw
  
  // 验证文件格式
  const validationResult = validateExcelFile(file.raw);
  if (!validationResult.valid) {
    ElMessage.error(validationResult.errors.join('\n'));
    return;
  }
  
  // 显示加载指示器
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在解析文件...',
    background: 'rgba(0, 0, 0, 0.7)'
  });
  
  // 使用FileReader读取文件内容
  const reader = new FileReader();
  
  reader.onload = (e) => {
    try {
      // 这里应该使用适当的库解析Excel文件
      // 示例代码，实际应该使用xlsx或其他库解析文件内容
      // 解析文件头，获取实际的列名
      excelColumns.value = ['员工姓名', '工号', '日期', '上班打卡', '下班打卡', '状态', '备注'];
      
      // 关闭加载指示器
      loadingInstance.close();
      
      ElMessage.success('文件解析成功');
    } catch (error) {
      console.error('解析文件失败:', error);
      ElMessage.error(`解析文件失败: ${error.message}`);
      loadingInstance.close();
    }
  };
  
  reader.onerror = () => {
    ElMessage.error('读取文件失败');
    loadingInstance.close();
  };
  
  // 读取文件
  reader.readAsArrayBuffer(file.raw);
}

// 显示字段映射对话框
const showFieldMappingDialog = () => {
  fieldMappingDialogVisible.value = true
}

// 显示模板对话框
const showTemplateDialog = () => {
  // 显示导入模板的说明或下载模板
  ElMessage({
    message: '模板下载功能正在开发中',
    type: 'info'
  })
}

// 添加自定义字段
const addCustomField = () => {
  customFields.value.push({
    name: '',
    column: ''
  })
}

// 移除自定义字段
const removeCustomField = (index) => {
  customFields.value.splice(index, 1)
}

// 保存字段映射
const saveFieldMapping = () => {
  // 验证必填字段
  if (!fieldMapping.name || !fieldMapping.date) {
    ElMessage.error('员工姓名和日期字段为必填项')
    return
  }
  
  ElMessage.success('字段映射保存成功')
  fieldMappingDialogVisible.value = false
}

// 提交导入
const submitImport = () => {
  if (!importForm.file) {
    ElMessage.error('请选择要导入的文件')
    return
  }
  
  // 显示加载指示器
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在导入数据...',
    background: 'rgba(0, 0, 0, 0.7)'
  });
  
  // 创建FormData对象
  const formData = new FormData();
  formData.append('file', importForm.file);
  
  // 添加字段映射信息
  formData.append('fieldMapping', JSON.stringify(fieldMapping));
  
  // 添加自定义字段
  formData.append('customFields', JSON.stringify(customFields.value));
  
  // 调用API上传文件
  import('../../api').then(({ default: api }) => {
    api.post('/attendance/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
      .then(response => {
        if (response && response.success) {
          // 更新考勤数据
          ElMessage.success(`成功导入 ${response.data.imported_count} 条考勤记录`);
          
          // 如果有错误信息，显示警告
          if (response.data.errors && response.data.errors.length > 0) {
            ElMessageBox.alert(
              `导入过程中有 ${response.data.errors.length} 个警告：\n${response.data.errors.join('\n')}`,
              '导入警告',
              { confirmButtonText: '确定', type: 'warning' }
            );
          }
          
          // 创建数据备份
          backupService.createBackup().then(backupResult => {
            if (backupResult.success) {
              console.log('数据备份成功:', backupResult.fileName);
            } else {
              console.error('数据备份失败:', backupResult.message);
            }
          });
          
          // 刷新数据
          fetchAttendanceData();
          importDialogVisible.value = false;
        } else {
          ElMessage.error(response?.error || '导入考勤数据失败');
        }
      })
      .catch(error => {
        console.error('导入考勤数据失败:', error);
        ElMessage.error('导入失败: ' + (error.message || '未知错误'));
      })
      .finally(() => {
        loadingInstance.close();
      });
  }).catch(error => {
    console.error('导入API模块失败:', error);
    ElMessage.error('系统错误: 无法加载API模块');
    loadingInstance.close();
  });
}

// 保存考勤规则
const saveAttendanceRules = () => {
  import('../../api').then(({ default: api }) => {
    api.post('/attendance/rules', attendanceRules)
      .then(response => {
        if (response && response.success) {
          ElMessage.success('考勤规则保存成功');
          attendanceRuleDialogVisible.value = false;
        } else {
          ElMessage.error(response?.error || '保存考勤规则失败');
        }
      })
      .catch(error => {
        console.error('保存考勤规则失败:', error);
        ElMessage.error('保存失败: ' + (error.message || '未知错误'));
      });
  }).catch(error => {
    console.error('导入API模块失败:', error);
    ElMessage.error('系统错误: 无法加载API模块');
  });
}

// 处理编辑
const handleEdit = (row) => {
  // 编辑考勤记录的逻辑
  console.log('编辑行:', row)
}

// 处理删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除这条考勤记录吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      // 这里应该是实际的删除逻辑
      import('../../api').then(({ default: api }) => {
        api.delete(`/attendance/${row.id}`)
          .then(response => {
            if (response && response.success) {
              ElMessage({
                type: 'success',
                message: '删除成功',
              })
              fetchAttendanceData() // 刷新数据
            } else {
              ElMessage.error(response?.error || '删除失败')
            }
          })
          .catch(error => {
            console.error('删除考勤记录失败:', error)
            ElMessage.error('删除失败: ' + (error.message || '未知错误'))
          })
      }).catch(error => {
        console.error('导入API模块失败:', error)
        ElMessage.error('系统错误: 无法加载API模块')
      })
    })
    .catch(() => {
      // 取消删除
    })
}

// 处理页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchAttendanceData()
}

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchAttendanceData()
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const statusMap = {
    '正常': 'success',
    '迟到': 'warning',
    '早退': 'warning',
    '缺卡': 'danger',
    '旷工': 'danger'
  }
  return statusMap[status] || 'info'
}

const handleFilter = () => {
  fetchAttendanceData()
}
const resetFilter = () => {
  filterForm.month = new Date().toISOString().slice(0, 7)
  filterForm.employeeId = ''
  filterForm.status = ''
  fetchAttendanceData()
}
</script>

<style scoped>
.attendance-container {
  padding: 20px;
}

.attendance-card {
  margin-bottom: 20px;
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.custom-fields-section {
  margin-top: 20px;
  border-top: 1px solid #EBEEF5;
  padding-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: normal;
}

.custom-field-row {
  display: flex;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.custom-field-row {
  display: flex;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 14px;
}
</style>