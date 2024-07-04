<template>
  <div>
    <job-card
      v-if="job.status"
      :id="this.$route.params.jobid"
      :status="job.status"
      :result="job.result"
      :started-at="job.started_at"
      :ended-at="job.ended_at"
      class="mt-4"
    />
    <log-container v-if="job.log?.length > 0" :logs="job.log" class="mt-4" />
  </div>
</template>
<script>
import { API } from '@/services/api'
import JobCard from '@/components/JobCard.vue'
import LogContainer from '@/components/LogContainer.vue'

export default {
  components: { JobCard, LogContainer },
  data() {
    return {
      job: {}
    }
  },
  methods: {
    async fetchJob(id) {
      const response = await API.scheduler.getJob(id)
      if (response.data) {
        this.job = response.data
      }
    }
  },
  mounted() {
    this.fetchJob(this.$route.params.jobid)
  }
}
</script>
