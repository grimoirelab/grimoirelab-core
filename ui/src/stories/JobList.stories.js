import JobList from '@/components/JobList.vue'

export default {
  title: 'Components/JobList',
  component: JobList,
  tags: ['autodocs']
}

export const Default = {
  args: {
    jobs: [
      {
        job_id: '444927b6-6c1a-40b1-b006-9addf93eb0ab',
        job_status: 'failed',
        startedAt: '2024-04-11T13:42:19.968',
        endedAt: '2024-04-11T17:00:00.968'
      },
      {
        job_id: '255eeabb-d3e5-4d8b-a8da-b8164737d00c',
        job_status: 'finished',
        startedAt: '2024-04-11T13:42:19.968',
        endedAt: '2024-04-11T13:50:24.968'
      },
      {
        job_id: '15767bc3-c8d1-4bb2-8a69-6d864f0387aa',
        job_status: 'started'
      },
      {
        job_id: '37ac515d-cdad-413a-a165-355db7d8f776',
        job_status: 'scheduled'
      }
    ]
  }
}
