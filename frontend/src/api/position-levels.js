import request from '@/utils/request'

// 职级类型API
export function getLevelTypes() {
  return request({
    url: '/api/position-levels/types',
    method: 'get'
  })
}

export function createLevelType(data) {
  return request({
    url: '/api/position-levels/types',
    method: 'post',
    data
  })
}

export function updateLevelType(id, data) {
  return request({
    url: `/api/position-levels/types/${id}`,
    method: 'put',
    data
  })
}

export function deleteLevelType(id) {
  return request({
    url: `/api/position-levels/types/${id}`,
    method: 'delete'
  })
}

// 职级API
export function getPositionLevels(typeId) {
  return request({
    url: '/api/position-levels/levels',
    method: 'get',
    params: typeId ? { type_id: typeId } : {}
  })
}

export function createPositionLevel(data) {
  return request({
    url: '/api/position-levels/levels',
    method: 'post',
    data
  })
}

export function updatePositionLevel(id, data) {
  return request({
    url: `/api/position-levels/levels/${id}`,
    method: 'put',
    data
  })
}

export function deletePositionLevel(id) {
  return request({
    url: `/api/position-levels/levels/${id}`,
    method: 'delete'
  })
} 