<template>
  <job-list v-if="task.jobs" :jobs="task.jobs" class="mt-4" />
</template>
<script>
import JobList from '@/components/JobList.vue'
export default {
  components: { JobList },
  props: {
    task: {
      type: Object,
      required: false,
      default: () => {}
    }
  }
}
</script>
