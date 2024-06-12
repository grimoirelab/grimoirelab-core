<template>
  <v-container>
    <div v-if="isLoading" class="d-flex justify-center align-center">
      <v-progress-circular :size="50" color="primary" indeterminate />
    </div>
    <v-alert v-if="error" type="error" variant="tonal">
      {{ error }}
    </v-alert>
    <div class="pa-4 border-thin bg-surface" v-if="repositories.length > 0">
      <p class="text-h6 mb-4">
        Found {{ repositories.length }} repositories for {{ backend }} user <code>{{ owner }}</code>
      </p>
      <repository-table
        :repositories="repositories"
        height="50vh"
        @update:selected="selected = $event"
      />
      <v-form ref="form">
        <fieldset class="mt-6">
          <legend class="text-subtitle-2 mb-2">Schedule interval</legend>
          <v-radio-group v-model="interval" color="primary" density="comfortable" hide-details>
            <v-radio :value="86400" label="Every day"></v-radio>
            <v-radio :value="604800" label="Every week"></v-radio>
            <v-radio value="custom" label="Custom"></v-radio>
          </v-radio-group>
          <v-row>
            <v-col cols="3">
              <v-text-field
                v-model="customInterval"
                class="mt-2 ml-8"
                color="primary"
                density="compact"
                hide-details="auto"
                label="Every"
                type="number"
                :rules="rules.customInterval"
              >
                <template #append>
                  <span class="text-medium-emphasis">seconds</span>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </fieldset>
        <v-btn
          :disabled="selected.length === 0"
          :loading="isLoading"
          class="mt-6"
          color="primary"
          size="default"
          variant="flat"
          @click="onSave"
        >
          Save
        </v-btn>
      </v-form>
    </div>
    <v-snackbar v-model="snackbar.open" color="success" :timeout="5000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>
<script>
import { API } from '@/services/api'
import RepositoryTable from '@/components/RepositoryTable.vue'

export default {
  components: { RepositoryTable },
  data() {
    return {
      backend: null,
      error: null,
      isLoading: true,
      pollInterval: null,
      repositories: [],
      selected: [],
      status: null,
      interval: 86400,
      customInterval: '',
      rules: {
        customInterval: [
          (value) => {
            if (this.interval == 'custom' && !value) return 'Enter an interval.'
            return true
          }
        ]
      },
      owner: null,
      snackbar: {
        open: false,
        text: ''
      }
    }
  },
  computed: {
    jobID() {
      return this.$route.params.jobid
    }
  },
  methods: {
    async fetchJob(jobId) {
      try {
        const response = await API.scheduler.getOwnerJob(jobId)
        this.status = response.data.status
        if (this.status == 'finished') {
          clearInterval(this.pollInterval)
          this.isLoading = false
          this.repositories = response.data.result.repositories
          this.backend = response.data.result.backend
          this.owner = response.data.result.owner
          if (response.data.result.errors.length > 0) {
            this.error = response.data.result.errors.join('. ')
          }
        } else if (this.status == 'failed') {
          clearInterval(this.pollInterval)
          this.isLoading = false
          this.error = 'Error'
        }
      } catch (error) {
        this.isLoading = false
        this.error = error.response?.data?.error_message || error
        clearInterval(this.pollInterval)
      }
    },
    async poll(jobId) {
      if (this.status != 'finished') {
        this.pollInterval = setInterval(this.fetchJob, 1000, jobId)
        setTimeout(() => {
          clearInterval(this.pollInterval)
        }, 600000)
      }
    },
    async onSave() {
      const { valid } = await this.$refs.form.validate()

      if (!valid) return
      this.isLoading = true
      const interval = this.interval === 'custom' ? this.customInterval : this.interval
      const responses = await Promise.all(
        this.selected.map((task) =>
          API.scheduler.create({
            taskData: {
              backend: task.category === 'commit' ? 'git' : this.backend,
              backendArgs: {
                uri: task.url
              },
              category: task.category
            },
            schedulerArgs: {
              interval: interval
            }
          })
        )
      )
      this.isLoading = false
      const OKresponses = responses.filter((response) => response.statusText === 'OK')
      this.snackbar = {
        open: true,
        text: `Scheduled ${OKresponses.length} tasks correctly`
      }
    }
  },
  mounted() {
    this.poll(this.jobID)
  }
}
</script>
<style lang="scss" scoped>
fieldset {
  border: 0;
}
</style>
