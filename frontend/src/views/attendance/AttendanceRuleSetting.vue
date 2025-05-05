<template>
  <div class="attendance-rule-setting-container">
    <el-card>
      <h2>考勤规则设置</h2>
      <el-form :model="form" label-width="120px" class="attendance-rule-form">
        <el-form-item label="考勤异常项">
          <el-button type="primary" @click="addRule">添加异常项</el-button>
        </el-form-item>
        <div v-for="(rule, idx) in form.rules" :key="rule.id" class="attendance-rule-item">
          <el-row :gutter="10">
            <el-col :span="5">
              <el-input v-model="rule.name" placeholder="异常项名称，如迟到、旷工等" />
            </el-col>
            <el-col :span="5">
              <el-select v-model="rule.chargeType" placeholder="扣款方式" @change="onChargeTypeChange(rule)">
                <el-option label="按次扣款" value="byTimes" />
                <el-option label="按天扣款" value="byDays" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <template v-if="rule.chargeType === 'byTimes'">
                <el-input-number v-model="rule.freeTimes" :min="0" label="免扣款次数" placeholder="免扣款次数" style="width:120px" />
                <span style="margin:0 8px;">次后，每次扣款</span>
                <el-input-number v-model="rule.amountPerTime" :min="0" label="每次扣款金额" style="width:120px" />
                <span>元</span>
                <el-tooltip effect="dark" content="如：迟到3次后，每次扣款20元" placement="top">
                  <el-icon style="margin-left:6px"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <template v-else-if="rule.chargeType === 'byDays'">
                <el-input v-model="rule.formula" placeholder="请输入扣款公式" style="width:300px" />
                <el-tooltip effect="dark" content="如：旷工扣除金额=(基本工资+绩效工资)/应出勤天数*旷工天数" placement="top">
                  <el-icon style="margin-left:6px"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
            </el-col>
            <el-col :span="2">
              <el-button type="danger" icon="Delete" @click="removeRule(idx)" circle />
            </el-col>
          </el-row>
        </div>
        <el-form-item>
          <el-button type="primary" @click="saveRules">保存规则</el-button>
        </el-form-item>
      </el-form>
      <el-divider />
      <div>
        <h4>示例说明：</h4>
        <ul>
          <li>迟到：免扣款3次，超过后每次扣款20元。</li>
          <li>旷工：按天扣款，公式为：(基本工资+绩效工资)/应出勤天数*旷工天数。</li>
          <li>自定义异常项：可选择按次或按天扣款，并设置相应金额或公式。</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled, Delete } from '@element-plus/icons-vue'

const defaultRules = [
  { id: 1, name: '迟到', chargeType: 'byTimes', freeTimes: 3, amountPerTime: 20, formula: '' },
  { id: 2, name: '早退', chargeType: 'byTimes', freeTimes: 2, amountPerTime: 15, formula: '' },
  { id: 3, name: '旷工', chargeType: 'byDays', freeTimes: 0, amountPerTime: 0, formula: '(基本工资+绩效工资)/应出勤天数*旷工天数' },
  { id: 4, name: '病假', chargeType: 'byDays', freeTimes: 0, amountPerTime: 0, formula: '(基本工资+绩效工资)/应出勤天数*病假天数*0.5' }
]

const form = ref({
  rules: JSON.parse(localStorage.getItem('attendanceRules') || 'null') || defaultRules
})

function addRule() {
  form.value.rules.push({
    id: Date.now(),
    name: '',
    chargeType: 'byTimes',
    freeTimes: 0,
    amountPerTime: 0,
    formula: ''
  })
}

function removeRule(idx) {
  form.value.rules.splice(idx, 1)
}

function onChargeTypeChange(rule) {
  if (rule.chargeType === 'byTimes') {
    rule.formula = ''
    rule.freeTimes = 0
    rule.amountPerTime = 0
  } else {
    rule.formula = ''
    rule.freeTimes = 0
    rule.amountPerTime = 0
  }
}

function saveRules() {
  localStorage.setItem('attendanceRules', JSON.stringify(form.value.rules))
  ElMessage.success('考勤规则已保存！')
}
</script>

<style scoped>
.attendance-rule-setting-container {
  padding: 24px;
}
.attendance-rule-form {
  margin-top: 20px;
}
.attendance-rule-item {
  margin-bottom: 18px;
  background: #f7f8fa;
  padding: 12px 8px 8px 8px;
  border-radius: 6px;
}
</style>