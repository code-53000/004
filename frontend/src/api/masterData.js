import request from '../utils/request'

export function getVillages() {
  return request({
    url: '/master-data/villages',
    method: 'get'
  })
}

export function createVillage(data) {
  return request({
    url: '/master-data/villages',
    method: 'post',
    data
  })
}

export function updateVillage(id, data) {
  return request({
    url: `/master-data/villages/${id}`,
    method: 'put',
    data
  })
}

export function deleteVillage(id) {
  return request({
    url: `/master-data/villages/${id}`,
    method: 'delete'
  })
}

export function getWellTypes() {
  return request({
    url: '/master-data/well-types',
    method: 'get'
  })
}

export function createWellType(data) {
  return request({
    url: '/master-data/well-types',
    method: 'post',
    data
  })
}

export function updateWellType(id, data) {
  return request({
    url: `/master-data/well-types/${id}`,
    method: 'put',
    data
  })
}

export function deleteWellType(id) {
  return request({
    url: `/master-data/well-types/${id}`,
    method: 'delete'
  })
}

export function getWaterQualityStandards(params) {
  return request({
    url: '/master-data/water-quality-standards',
    method: 'get',
    params
  })
}

export function createWaterQualityStandard(data) {
  return request({
    url: '/master-data/water-quality-standards',
    method: 'post',
    data
  })
}

export function updateWaterQualityStandard(id, data) {
  return request({
    url: `/master-data/water-quality-standards/${id}`,
    method: 'put',
    data
  })
}

export function deleteWaterQualityStandard(id) {
  return request({
    url: `/master-data/water-quality-standards/${id}`,
    method: 'delete'
  })
}
