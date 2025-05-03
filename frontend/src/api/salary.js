import request from '@/utils/request'

// 薪酬项API
export function getSalaryItems() {
  return request({
    url: '/api/salary-items/items',
    method: 'get'
  })
}

export function createSalaryItem(data) {
  return request({
    url: '/api/salary-items/items',
    method: 'post',
    data
  })
}

export function updateSalaryItem(id, data) {
  return request({
    url: `/api/salary-items/items/${id}`,
    method: 'put',
    data
  })
}

export function deleteSalaryItem(id) {
  return request({
    url: `/api/salary-items/items/${id}`,
    method: 'delete'
  })
}

// 匹配规则API
export function getMatchingRules() {
  return request({
    url: '/api/salary-items/rules',
    method: 'get'
  })
}

export function createMatchingRule(data) {
  return request({
    url: '/api/salary-items/rules',
    method: 'post',
    data
  })
}

export function updateMatchingRule(id, data) {
  return request({
    url: `/api/salary-items/rules/${id}`,
    method: 'put',
    data
  })
}

export function deleteMatchingRule(id) {
  return request({
    url: `/api/salary-items/rules/${id}`,
    method: 'delete'
  })
} 