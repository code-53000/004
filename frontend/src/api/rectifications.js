import request from '../utils/request'

export function getRectifications(params) {
  return request({
    url: '/rectifications',
    method: 'get',
    params
  })
}

export function getRectification(id) {
  return request({
    url: `/rectifications/${id}`,
    method: 'get'
  })
}

export function createRectification(data) {
  return request({
    url: '/rectifications',
    method: 'post',
    data
  })
}

export function updateRectification(id, data) {
  return request({
    url: `/rectifications/${id}`,
    method: 'put',
    data
  })
}

export function deleteRectification(id) {
  return request({
    url: `/rectifications/${id}`,
    method: 'delete'
  })
}
