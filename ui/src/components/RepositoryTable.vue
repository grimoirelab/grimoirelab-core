<template>
  <v-data-table-virtual
    v-if="items.length > 0"
    v-model="selected"
    :fixed-header="true"
    :headers="headers"
    :items="items"
    :loading="isLoading"
    color="primary"
    item-value="url"
    return-object
    show-select
    @update:modelValue="$emit('update:selected', selectedByCategory)"
  >
    <template #top>
      <div class="d-flex align-center justify-space-between pa-1">
        <p class="text-subtitle-2">Select the data you want to analyse</p>
        <div class="d-flex">
          <v-switch
            v-model="filters.archived"
            class="mr-4"
            color="primary"
            label="Show archived repositories"
            hide-details
          />
          <v-switch
            v-model="filters.fork"
            color="primary"
            label="Show forked repositories"
            hide-details
          ></v-switch>
        </div>
      </div>
    </template>
    <template #item.url="{ item }">
      {{ item.url }}
      <v-chip v-if="item.fork" class="ml-2" color="primary" density="comfortable" size="small">
        <v-icon size="small" start>mdi-source-fork</v-icon>
        fork
      </v-chip>
      <v-chip v-if="item.archived" class="ml-2" color="warning" density="comfortable" size="small">
        <v-icon size="small" start>mdi-archive-outline</v-icon>
        archived
      </v-chip>
    </template>
    <template #item.commit="{ item }">
      <v-checkbox-btn
        v-model="item.form.commit"
        color="primary"
        density="compact"
        @update:modelValue="$emit('update:selected', selectedByCategory)"
      />
    </template>
    <template #item.issue="{ item }">
      <v-checkbox-btn
        v-model="item.form.issue"
        :disabled="!item.has_issues"
        color="primary"
        density="compact"
        @update:modelValue="$emit('update:selected', selectedByCategory)"
      />
    </template>
    <template #item.pr="{ item }">
      <v-checkbox-btn
        v-model="item.form.pr"
        :disabled="!item.has_pull_requests"
        color="primary"
        density="compact"
        @update:modelValue="$emit('update:selected', selectedByCategory)"
      />
    </template>
  </v-data-table-virtual>
</template>
<script>
export default {
  name: 'RepositoryTable',
  emits: ['update:selected'],
  props: {
    repositories: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      isLoading: false,
      items: [],
      headers: [
        { title: 'Repository URL', value: 'url' },
        { title: 'Fetch commits', value: 'commit' },
        { title: 'Fetch issues', value: 'issue' },
        { title: 'Fetch pull requests', value: 'pr' }
      ],
      selected: [],
      filters: {
        archived: true,
        fork: true
      }
    }
  },
  computed: {
    selectedByCategory() {
      return this.selected.reduce((list, current) => {
        Object.entries(current.form).forEach((category) => {
          const [key, value] = category
          if (value) {
            list.push({
              category: key,
              url: key === 'commit' ? `${current.url}.git` : current.url
            })
          }
        })
        return list
      }, [])
    }
  },
  methods: {
    applyFilters(array, filters) {
      this.selected = []
      const filterKeys = Object.keys(filters)
      return array.reduce((acc, item) => {
        const match = filterKeys.every((key) => {
          if (filters[key]) return true
          return filters[key] === item[key]
        })
        if (match) {
          acc.push({
            ...item,
            form: {
              commit: true,
              pr: item.has_pull_requests,
              issue: item.has_issues
            }
          })
        }
        return acc
      }, [])
    }
  },
  watch: {
    filters: {
      handler(value) {
        this.items = this.applyFilters(this.repositories, value)
      },
      deep: true
    },
    repositories(value) {
      this.items = this.applyFilters(value, this.filters)
    }
  },
  mounted() {
    this.items = this.applyFilters(this.repositories, this.filters)
  }
}
</script>
<style lang="scss" scoped>
:deep(.v-switch) {
  .v-selection-control {
    min-height: auto;
  }
  .v-label {
    font-size: 0.875rem;
    letter-spacing: normal;
    font-weight: 500;
  }
}
</style>
