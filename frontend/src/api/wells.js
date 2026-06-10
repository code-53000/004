import request from '../utils/request'

export function getWells(params) {
  return request({
    url: '/wells',
    method: 'get',
    params
  })
}

export function getWell(id) {
  return request({
    url: `/wells/${id}`,
    method: 'get'
  })
}

export function createWell(data) {
  return request({
    url: '/wells',
    method: 'post',
    data
  })
}

export function updateWell(id, data) {
  return request({
    url: `/wells/${id}`,
    method: 'put',
    data
  })
}

export function deleteWell(id) {
  return request({
    url: `/wells/${id}`,
    method: 'delete'
  })
}
