import request from '../utils/request'

export function getInspections(params) {
  return request({
    url: '/inspections',
    method: 'get',
    params
  })
}

export function getInspection(id) {
  return request({
    url: `/inspections/${id}`,
    method: 'get'
  })
}

export function createInspection(data) {
  return request({
    url: '/inspections',
    method: 'post',
    data
  })
}

export function updateInspection(id, data) {
  return request({
    url: `/inspections/${id}`,
    method: 'put',
    data
  })
}

export function deleteInspection(id) {
  return request({
    url: `/inspections/${id}`,
    method: 'delete'
  })
}
