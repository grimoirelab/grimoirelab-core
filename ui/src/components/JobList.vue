<template>
  <div>
    <h2 class="text-h6 mb-4">
      Jobs
      <v-chip class="ml-2" density="comfortable">
        {{ jobs.length }}
      </v-chip>
    </h2>
    <status-card
      v-for="(job, index) in jobs"
      :key="job.job_id"
      :status="job.job_status"
      :to="{
        name: 'job',
        params: { jobid: job.job_id }
      }"
      class="mb-2"
    >
      <v-row>
        <v-col>
          <v-card-title class="text-subtitle-2 pb-0">
            {{ job.job_id }}
            <v-chip :color="job.job_status" class="ml-3" density="comfortable" size="small">
              {{ job.job_status }}
            </v-chip>
          </v-card-title>
          <v-card-subtitle class="pb-2"> #{{ index + 1 }} </v-card-subtitle>
        </v-col>
        <v-col cols="4">
          <p v-if="job.endedAt" class="px-4 pt-2 text-body-2">
            <v-icon color="medium-emphasis" size="small" start> mdi-calendar </v-icon>
            {{ formatDate(job.endedAt) }}
          </p>
          <p v-if="job.endedAt" class="px-4 py-2 text-body-2">
            <v-icon color="medium-emphasis" size="small" start> mdi-alarm </v-icon>
            {{ getDuration(job.startedAt, job.endedAt) }}
          </p>
          <p v-else-if="job.job_status === 'started'" class="px-4 py-2 text-body-2">
            <v-icon color="medium-emphasis" size="small" start> mdi-alarm </v-icon>
            In progress
          </p>
        </v-col>
      </v-row>
    </status-card>
  </div>
</template>
<script>
import { formatDate, getDuration } from '@/utils/dates'
import StatusCard from '@/components/StatusCard.vue'

export default {
  name: 'JobList',
  components: { StatusCard },
  props: {
    jobs: {
      type: Array,
      required: true
    }
  },
  methods: {
    formatDate,
    getDuration
  }
}
</script>
<style lang="scss" scoped>
.v-card .v-card-title {
  line-height: 1.7rem;
}
</style>
