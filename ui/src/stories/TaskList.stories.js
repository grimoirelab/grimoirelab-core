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
    total_pages: 1,
    tasks: [
      {
        uuid: '09007426-f752-4844-b8d8-88618ee34b58',
        status: 'recovery',
        runs: 2,
        failures: 1,
        last_run: '2024-11-13T15:35:15.705200Z',
        scheduled_at: '2024-11-13T15:35:09.148717Z',
        datasource_type: 'git',
        datasource_category: 'commit'
      },
      {
        uuid: 'http://localhost:8000/scheduler/tasks/?page=1',
        status: 'enqueued',
        runs: 8,
        failures: 0,
        last_run: '2024-11-13T15:42:56.610901Z',
        scheduled_at: '2024-11-14T15:35:09.148717Z',
        datasource_type: 'git',
        datasource_category: 'commit'
      }
    ]
  }
}
