<template>
  <v-container>
    <task-card
      v-if="task.id"
      :id="task.id"
      :age="task.age"
      :backend="task.backend"
      :backend-args="task.backend_args"
      :category="task.category"
      :status="task.status?.toLowerCase()"
      :executions="task.executions"
      :interval="task.interval"
      :last-execution="task.last_execution"
      :max-retries="task.max_retries"
      :scheduled-date="task.scheduled_datetime"
      class="mt-4"
    />
    <router-view :task="task"></router-view>
  </v-container>
</template>
<script>
import { API } from '@/services/api'
import TaskCard from '@/components/TaskCard.vue'

export default {
  components: { TaskCard },
  data() {
    return {
      task: {}
    }
  },
  mounted() {
    this.fetchTask(this.$route.params.id)
  },
  methods: {
    async fetchTask(id) {
      const response = await API.scheduler.get(id)
      if (response.data) {
        this.task = response.data
      }
    }
  }
}
</script>
