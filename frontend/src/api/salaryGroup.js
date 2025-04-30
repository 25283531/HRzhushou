// 薪资组API服务
import api from './index'

// 薪资组API
export const salaryGroupApi = {
  // 获取所有薪资组
  getAllGroups() {
    return api.get('/salary-groups')
  },
  
  // 获取单个薪资组详情
  getGroupById(id) {
    return api.get(`/salary-groups/${id}`)
  },
  
  // 创建薪资组
  createGroup(data) {
    return api.post('/salary-groups', data)
  },
  
  // 更新薪资组
  updateGroup(id, data) {
    return api.put(`/salary-groups/${id}`, data)
  },
  
  // 删除薪资组
  deleteGroup(id) {
    return api.delete(`/salary-groups/${id}`)
  },
  
  // 获取薪资组下的薪酬项
  getGroupItems(groupId) {
    return api.get(`/salary-groups/${groupId}/items`)
  },
  
  // 创建薪酬项
  createItem(groupId, data) {
    return api.post(`/salary-groups/${groupId}/items`, data)
  },
  
  // 更新薪酬项
  updateItem(groupId, itemId, data) {
    return api.put(`/salary-groups/${groupId}/items/${itemId}`, data)
  },
  
  // 删除薪酬项
  deleteItem(groupId, itemId) {
    return api.delete(`/salary-groups/${groupId}/items/${itemId}`)
  },
  
  // 更新薪资组公式
  updateFormula(groupId, formula) {
    return api.put(`/salary-groups/${groupId}/formula`, { formula })
  },
  
  // 测试计算薪资公式
  calculateFormula(groupId, formula) {
    return api.post(`/salary-groups/${groupId}/calculate`, { formula })
  },
  
  // 获取薪资组匹配规则
  getGroupMatches(groupId) {
    return api.get(`/salary-groups/${groupId}/matches`)
  },
  
  // 添加薪资组匹配规则
  addGroupMatch(groupId, matchData) {
    return api.post(`/salary-groups/${groupId}/matches`, matchData)
  },
  
  // 删除薪资组匹配规则
  deleteGroupMatch(groupId, matchId) {
    return api.delete(`/salary-groups/${groupId}/matches/${matchId}`)
  }
}

// 公式计算工具
export const formulaUtils = {
  // 解析公式
  parseFormula(formula, items) {
    if (!formula || !items || items.length === 0) {
      return 0
    }
    
    try {
      // 创建薪酬项映射表
      const itemMap = {}
      items.forEach(item => {
        itemMap[item.name] = item.type === '收入' ? item.amount : -item.amount
      })
      
      // 替换公式中的薪酬项为实际金额
      let calculableFormula = formula
      for (const itemName in itemMap) {
        // 使用正则表达式确保完整匹配薪酬项名称
        const regex = new RegExp(itemName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
        calculableFormula = calculableFormula.replace(regex, itemMap[itemName])
      }
      
      // 替换中文括号为英文括号
      calculableFormula = calculableFormula.replace(/（/g, '(').replace(/）/g, ')')
      
      // 计算公式
      // eslint-disable-next-line no-eval
      const result = eval(calculableFormula)
      return typeof result === 'number' ? result : 0
    } catch (error) {
      console.error('公式计算错误:', error)
      return 0
    }
  },
  
  // 验证公式是否有效
  validateFormula(formula, items) {
    if (!formula) return false
    
    try {
      // 创建测试用的薪酬项映射表
      const itemMap = {}
      items.forEach(item => {
        itemMap[item.name] = item.type === '收入' ? item.amount : -item.amount
      })
      
      // 替换公式中的薪酬项为实际金额
      let calculableFormula = formula
      for (const itemName in itemMap) {
        const regex = new RegExp(itemName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')
        calculableFormula = calculableFormula.replace(regex, itemMap[itemName])
      }
      
      // 替换中文括号为英文括号
      calculableFormula = calculableFormula.replace(/（/g, '(').replace(/）/g, ')')
      
      // 尝试计算公式
      // eslint-disable-next-line no-eval
      eval(calculableFormula)
      return true
    } catch (error) {
      console.error('公式验证错误:', error)
      return false
    }
  }
}