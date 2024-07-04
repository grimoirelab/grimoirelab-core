import TaskList from '@/components/TaskList/TaskList.vue'

export default {
  title: 'Components/TaskList',
  component: TaskList,
  tags: ['autodocs']
}

export const Default = {
  args: {
    count: 2,
    pages: 1,
    tasks: [
      {
        id: 1,
        backend: 'git',
        backend_args: {
          uri: 'https://github.com/chaoss/grimoirelab.git'
        },
        category: 'commit',
        status: 'enqueued',
        executions: 3,
        jobs: [
          {
            job_id: '15767bc3-c8d1-4bb2-8a69-6d864f0387aa',
            job_status: 'scheduled'
          },
          {
            job_id: '77708428-596d-4867-9dec-03f35ef6a02a',
            job_status: 'finished'
          },
          {
            job_id: '4bc100e7-9428-4890-8344-216faf4882b3',
            job_status: 'finished'
          },
          {
            job_id: '3ffcef1c-ab3c-4a97-939d-968ba7ced4a0',
            job_status: 'finished'
          }
        ],
        scheduled_datetime: '2024-04-16T10:01:42.431Z',
        last_execution: '2024-04-15T10:01:42.431Z'
      },
      {
        id: 2,
        backend: 'git',
        backend_args: {
          uri: 'https://github.com/grimoirelab/grimoirelab-core.git'
        },
        category: 'commit',
        status: 'enqueued',
        executions: 2,
        jobs: [
          {
            job_id: '15767bc3-c8d1-4bb2-8a69-6d864f0387aa',
            job_status: 'scheduled'
          },
          {
            job_id: '77708428-596d-4867-9dec-03f35ef6a02a',
            job_status: 'finished'
          },
          {
            job_id: '4bc100e7-9428-4890-8344-216faf4882b3',
            job_status: 'failed'
          }
        ],
        scheduled_datetime: '2024-04-22T10:49:10.937Z',
        last_execution: '2024-04-15T10:49:10.937Z'
      }
    ]
  }
}
