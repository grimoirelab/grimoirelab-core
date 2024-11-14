import axios from 'axios'

const base = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000'

export const scheduler = {
  list: (params) => axios.get(`${base}/scheduler/list`, { params }),
  get: (taskId) => axios.get(`${base}/scheduler/task/${taskId}`),
  create: (data) => axios.post(`${base}/scheduler/add_task`, data),
  delete: (taskId) => axios.post(`${base}/scheduler/remove_task`, { taskId }),
  reschedule: (taskId) => axios.post(`${base}/scheduler/reschedule_task`, { taskId }),
  getJob: (jobId) => axios.get(`${base}/scheduler/job/${jobId}`)
}
