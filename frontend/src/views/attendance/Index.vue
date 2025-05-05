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
          <el-input v-model="filterForm.employeeName" placeholder="请输入员工姓名" clearable />
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
      width="700px">
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="考勤数据文件">
          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".xlsx,.xls">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                仅支持Excel格式文件（.xlsx/.xls）
              </div>
            </template>
          </el-upload>
          <el-button type="success" style="margin-left: 20px" @click="downloadTemplate">下载模板</el-button>
        </el-form-item>
        <el-form-item v-if="sheetNames.length > 1" label="选择工作表">
          <el-select v-model="selectedSheet" placeholder="请选择要导入的工作表" style="width: 250px">
            <el-option v-for="name in sheetNames" :key="name" :label="name" :value="name" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="sheetPreview.length" label="表格预览">
          <el-table :data="sheetPreview" border height="200" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col" :prop="col" :label="col" />
          </el-table>
        </el-form-item>
        <el-form-item v-if="mappingStep && importForm.file && selectedSheet && Array.isArray(fieldMappings) && fieldMappings.length > 0" label="字段映射">
          <el-table :data="fieldMappings" border style="width: 100%">
            <el-table-column prop="dbField" label="计算字段" width="180">
              <template #default="{ row }">
                {{ dbFields.find(f => f.dbField === row.dbField)?.label || row.dbField }}
              </template>
            </el-table-column>
            <el-table-column label="Excel列名">
              <template #default="{ row: scope }">
                <el-select v-model="scope.row.excelField" placeholder="请选择Excel列名" style="width: 200px">
                  <el-option v-for="col in previewColumns" :key="col" :label="col" :value="col" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button v-if="!mappingStep && sheetPreview.length" type="primary" @click="confirmMapping">下一步</el-button>
          <el-button v-if="mappingStep" type="primary" @click="submitImport">导入</el-button>
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
    

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import { parseDate, formatDate } from '../../utils/dateParser'
import { validateAttendanceRecords, validateExcelFile } from '../../utils/dataValidator'
import { processAttendanceData } from '../../utils/workerService'
import backupService from '../../utils/backupService'
import * as XLSX from 'xlsx'


// Excel相关变量，避免未定义错误
const selectedSheet = ref('')
const sheetNames = ref([])
const sheetPreview = ref([])
const previewColumns = ref([])
const mappingStep = ref(false)
const fieldMappings = ref([])

// 下载模板方法
const downloadTemplate = () => {
  // 构造包含所有字段的Excel模板数据
  const ws_data = [
    ['姓名', '工号', '身份证号', '考勤月份', '应出勤天数', '实际出勤天数', '迟到次数', '严重迟到次数', '早退次数', '严重早退次数', '旷工次数', '病假天数', '事假天数', '工伤休假天数', '休年假天数', '加班时长'],
    ['张三', '1001', '123456789012345678', '2024-05', '22', '22', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['李四', '1002', '987654321098765432', '2024-05', '22', '21', '1', '0', '0', '0', '0', '0', '0', '0', '0', '2']
  ];
  const ws = XLSX.utils.aoa_to_sheet(ws_data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, '考勤模板');
  XLSX.writeFile(wb, '考勤导入模板.xlsx');
}

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
const attendanceRules = ref([
  {
    lateDeduction: 0,
    lateFreeCount: 0,
    seriousLateDeduction: 0,
    seriousLateMinutes: 0,
    earlyLeaveDeduction: 0,
    missedPunchDeduction: 0,
    absentDeduction: 0
  }
])

// 员工数据
const employees = ref([])

// 筛选表单
const filterForm = reactive({
  month: new Date().toISOString().slice(0, 7), // 默认当前月份
  employeeName: ''
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
  loading.value = true;
  import('../../api').then(({ default: api }) => {
    api.get('/employee/list')
      .then(response => {
        if (response && response.success && response.data && Array.isArray(response.data.items)) {
          employees.value = response.data.items || [];
        } else {
          console.error('员工数据接口返回异常:', response);
          ElMessage.error(response?.error || '获取员工数据失败');
          employees.value = [];
        }
      })
      .catch(error => {
        console.error('获取员工数据失败:', error);
        ElMessage.error('获取员工数据失败: ' + (error.message || '未知错误'));
        employees.value = [];
      })
      .finally(() => {
        loading.value = false;
      });
  }).catch(error => {
    console.error('导入API模块失败:', error);
    ElMessage.error('系统错误: 无法加载API模块');
    loading.value = false;
  });
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
}

// 下一步：进入字段映射步骤
const confirmMapping = () => {
  // 检查 Excel 表头和数据库字段
  if (!Array.isArray(dbFields.value) || !Array.isArray(previewColumns.value) || previewColumns.value.length === 0) {
    ElMessage.error('请先上传并选择包含表头的Excel文件');
    fieldMappings.value = [];
    return;
  }
  // 生成映射数组，确保每项都包含 excelField 字段
  fieldMappings.value = dbFields.value.map(f => {
    return {
      dbField: f.dbField,
      excelField: previewColumns.value.includes(f.label) ? f.label : (previewColumns.value[0] || '')
    };
  });
  mappingStep.value = true;
};
const handleFileChange = (file) => {
  importForm.file = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      sheetNames.value = workbook.SheetNames
      if (sheetNames.value.length === 1) {
        selectedSheet.value = sheetNames.value[0]
        showSheetPreview(workbook, selectedSheet.value)
      } else {
        selectedSheet.value = ''
        sheetPreview.value = []
        previewColumns.value = []
      }
      mappingStep.value = false
      fieldMappings.value = []
      importForm.workbook = workbook
    } catch (err) {
      ElMessage.error('解析Excel文件失败: ' + err.message)
    }
  }
  reader.readAsArrayBuffer(file.raw)
}

watch(selectedSheet, (val) => {
  if (val && importForm.workbook) {
    showSheetPreview(importForm.workbook, val)
  }
})

function showSheetPreview(workbook, sheetName) {
  const ws = workbook.Sheets[sheetName]
  const json = XLSX.utils.sheet_to_json(ws, { header: 1 })
  if (json.length > 1) {
    previewColumns.value = json[0]
    sheetPreview.value = json.slice(1, 6).map(row => {
      const obj = {}
      previewColumns.value.forEach((col, idx) => {
        obj[col] = row[idx] || ''
      })
      return obj
    })
  } else {
    previewColumns.value = []
    sheetPreview.value = []
  }
}

// 动态获取考勤规则字段
const defaultRules = [
  { id: 1, name: '迟到', chargeType: 'byTimes', freeTimes: 3, amountPerTime: 20, formula: '' },
  { id: 2, name: '早退', chargeType: 'byTimes', freeTimes: 2, amountPerTime: 15, formula: '' },
  { id: 3, name: '旷工', chargeType: 'byDays', freeTimes: 0, amountPerTime: 0, formula: '(基本工资+绩效工资)/应出勤天数*旷工天数' },
  { id: 4, name: '病假', chargeType: 'byDays', freeTimes: 0, amountPerTime: 0, formula: '(基本工资+绩效工资)/应出勤天数*病假天数*0.5' }
]
const getAttendanceRules = () => {
  try {
    const rules = JSON.parse(localStorage.getItem('attendanceRules'))
    return Array.isArray(rules) && rules.length > 0 ? rules : defaultRules
  } catch {
    return defaultRules
  }
}
const dbFields = ref([
  { dbField: 'name', label: '员工姓名' },
  { dbField: 'number', label: '工号' },
  { dbField: 'idCard', label: '身份证号' },
  { dbField: 'month', label: '考勤月份' },
  { dbField: 'shouldWorkDays', label: '应出勤天数' },
  { dbField: 'actualWorkDays', label: '实际出勤天数' },
  ...getAttendanceRules().map(rule => ({ dbField: rule.name, label: rule.name }))
])
const resetImportDialog = () => {
  importForm.file = null;
  selectedSheet.value = '';
  sheetNames.value = [];
  sheetPreview.value = [];
  previewColumns.value = [];
  fieldMappings.value = [];
  fieldMapping.name = '';
  fieldMapping.number = '';
  fieldMapping.date = '';
  fieldMapping.checkIn = '';
  fieldMapping.checkOut = '';
  customFields.value = [];
  mappingStep.value = false;
};
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
    api.post('/attendance/rules', { rules: attendanceRules.value })
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
  // 动态生成状态与标签类型映射
  const rules = getAttendanceRules()
  const statusMap = { '正常': 'success' }
  rules.forEach(rule => {
    if (rule.name.includes('迟到') || rule.name.includes('早退')) {
      statusMap[rule.name] = 'warning'
    } else if (rule.name.includes('旷工') || rule.name.includes('缺卡')) {
      statusMap[rule.name] = 'danger'
    } else {
      statusMap[rule.name] = 'info'
    }
  })
  return statusMap[status] || 'info'
}

const handleFilter = () => {
  const name = filterForm.employeeName && filterForm.employeeName.trim();
  if (name) {
    // 判断员工花名册中是否有该员工
    const foundEmployee = employees.value.find(emp => emp.name === name);
    if (!foundEmployee) {
      ElMessage.warning('未查询到该员工，请重新输入');
      return;
    }
    // 判断考勤数据中是否有该员工
    const foundAttendance = attendanceData.value.find(item => item.employee_name === name);
    if (!foundAttendance) {
      ElMessage.info('花名册中有该员工，但是所选月份没有该员工的考勤数据');
      // 依然可以继续查询或刷新数据
    }
  }
  fetchAttendanceData();
}
const resetFilter = () => {
  filterForm.month = new Date().toISOString().slice(0, 7)
  filterForm.employeeName = ''
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