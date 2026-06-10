import request from '../utils/request'

export function getTestBatches(params) {
  return request({
    url: '/water-tests/batches',
    method: 'get',
    params
  })
}

export function getTestBatch(id) {
  return request({
    url: `/water-tests/batches/${id}`,
    method: 'get'
  })
}

export function createTestBatch(data) {
  return request({
    url: '/water-tests/batches',
    method: 'post',
    data
  })
}

export function addTestItem(batchId, data) {
  return request({
    url: `/water-tests/batches/${batchId}/items`,
    method: 'post',
    data
  })
}

export function getTestItems(params) {
  return request({
    url: '/water-tests/items',
    method: 'get',
    params
  })
}

export function deleteTestBatch(id) {
  return request({
    url: `/water-tests/batches/${id}`,
    method: 'delete'
  })
}

export function deleteTestItem(id) {
  return request({
    url: `/water-tests/items/${id}`,
    method: 'delete'
  })
}
