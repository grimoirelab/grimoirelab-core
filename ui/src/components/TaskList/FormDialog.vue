<template>
  <v-dialog v-model="isOpen" max-width="600">
    <template #activator="{ props: activatorProps }">
      <v-btn
        class="ml-auto"
        color="secondary"
        prepend-icon="mdi-plus"
        text="Add"
        variant="flat"
        v-bind="activatorProps"
      ></v-btn>
    </template>
    <v-card title="Schedule task">
      <v-btn-toggle v-model="selectedForm" class="mx-6 mt-4" color="primary" mandatory>
        <v-btn value="single" class="button--lowercase" size="small" variant="outlined">
          Add a repository
        </v-btn>
        <v-btn value="multiple" class="button--lowercase" size="small" variant="outlined">
          Load all from owner
        </v-btn>
      </v-btn-toggle>
      <v-form v-if="selectedForm === 'single'" ref="singleForm" class="pa-6">
        <fieldset>
          <legend class="text-subtitle-2 mb-3">Fetch data from a repository</legend>
          <div class="input-grid">
            <v-select
              v-model="formData.backend"
              :items="backends"
              item-title="backend"
              color="primary"
              density="compact"
            >
              <template #selection="{ item }">
                <v-icon size="small" start>
                  {{ 'mdi-' + item.title.toLowerCase() }}
                </v-icon>
                {{ item.title }}
              </template>
              <template #item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  :prepend-icon="`mdi-${item.title.toLowerCase()}`"
                  density="comfortable"
                  nav
                />
              </template>
            </v-select>
            <v-text-field
              v-model="formData.uri"
              label="Repository URL"
              color="primary"
              density="compact"
              :rules="rules.required"
            />
          </div>
        </fieldset>
        <fieldset class="mt-2">
          <legend class="text-subtitle-2 mb-2">Select the data that you want to analyze</legend>
          <v-checkbox
            v-for="(category, index) in categories"
            v-model="formData.categories"
            :key="formData.backend + category.value"
            :label="category.text"
            :value="category.value"
            color="primary"
            density="comfortable"
            :hide-details="index !== categories.length - 1"
            :rules="rules.category"
          />
        </fieldset>
        <fieldset class="mt-2">
          <legend class="text-subtitle-2 mb-2">Schedule interval</legend>
          <v-radio-group
            v-model="formData.interval"
            color="primary"
            density="comfortable"
            hide-details
          >
            <v-radio :value="86400" label="Every day"></v-radio>
            <v-radio :value="604800" label="Every week"></v-radio>
            <v-radio value="custom" label="Custom"></v-radio>
          </v-radio-group>
          <v-row>
            <v-col cols="6">
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
        <v-card-actions class="pt-0 pb-4 pr-0">
          <v-spacer></v-spacer>
          <v-btn text="Cancel" variant="plain" @click="closeModal"></v-btn>
          <v-btn color="primary" text="Save" variant="flat" @click="onSave"></v-btn>
        </v-card-actions>
      </v-form>
      <v-form v-else ref="multipleForm" class="pa-6">
        <p class="text-body-2 mb-5">
          Load all repositories from a GitHub or GitLab user or organization. You will be able to
          add all of their commits, pull requests and issues or review and select each one
          individually.
        </p>
        <div class="input-grid">
          <v-select
            v-model="formData.backend"
            :items="backends.filter((b) => b.owner)"
            item-title="backend"
            color="primary"
            density="compact"
          >
            <template #selection="{ item }">
              <v-icon size="small" start>
                {{ 'mdi-' + item.title.toLowerCase() }}
              </v-icon>
              {{ item.title }}
            </template>
            <template #item="{ props, item }">
              <v-list-item
                v-bind="props"
                :prepend-icon="`mdi-${item.title.toLowerCase()}`"
                density="comfortable"
                nav
              />
            </template>
          </v-select>
          <v-text-field
            v-model="formData.owner"
            label="User or organization"
            color="primary"
            density="compact"
          />
        </div>
        <v-card-actions class="pt-0 pb-4 pr-0">
          <v-spacer></v-spacer>
          <v-btn
            :disabled="!formData.owner"
            color="primary"
            variant="flat"
            size="default"
            class="ml-3"
            @click="onLoad"
          >
            Load
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>
<script>
const defaultData = {
  backend: 'GitHub',
  categories: [],
  uri: '',
  interval: 604800,
  owner: ''
}

export default {
  name: 'FormDialog',
  emits: ['create', 'load'],
  data() {
    return {
      isOpen: false,
      selectedForm: 'single',
      formData: { ...defaultData },
      customInterval: '',
      backends: [
        {
          backend: 'Git',
          categories: [{ text: 'Commits', value: 'commit' }],
          owner: false
        },
        {
          backend: 'GitHub',
          categories: [
            { text: 'Issues', value: 'issue' },
            { text: 'Pull Requests', value: 'prs' }
          ],
          owner: true
        },
        {
          backend: 'GitLab',
          categories: [
            { text: 'Issues', value: 'issue' },
            { text: 'Merge Requests', value: 'merge' }
          ],
          owner: true
        }
      ],
      rules: {
        required: [
          (value) => {
            if (value) return true

            return 'This field is required.'
          }
        ],
        category: [
          (value) => {
            if (value.length > 0) return true
            return 'Select at least one category.'
          }
        ],
        customInterval: [
          (value) => {
            if (this.formData.interval == 'custom' && !value) return 'Enter an interval.'
            return true
          }
        ]
      }
    }
  },
  computed: {
    categories() {
      return this.backends.find((item) => item.backend === this.formData.backend).categories
    },
    emitData() {
      return this.formData.categories.map((category) => ({
        taskData: {
          backend: this.formData.backend.toLowerCase(),
          backendArgs: {
            uri: this.formData.uri
          },
          category
        },
        schedulerArgs: {
          interval: this.formData.interval
        }
      }))
    }
  },
  methods: {
    async onSave() {
      const { valid } = await this.$refs.singleForm.validate()

      if (!valid) return

      if (this.formData.interval === 'custom') {
        this.formData.interval = this.customInterval
      }

      this.$emit('create', this.emitData)
      this.closeModal()
    },
    onLoad() {
      this.$emit('load', {
        owner: this.formData.owner,
        backend: this.formData.backend.toLowerCase()
      })
      this.closeModal()
    },
    closeModal() {
      this.isOpen = false
      this.resetForm()
    },
    resetForm() {
      this.formData = { ...defaultData }
      this.selectedForm = 'single'
    }
  },
  watch: {
    'formData.backend'() {
      Object.assign(this.formData, { categories: [] })
    }
  }
}
</script>
<style lang="scss" scoped>
.input-grid {
  display: grid;
  grid-template-columns: 0.7fr 2fr;

  :deep(.v-select) .v-field {
    border-radius: 4px 0 0 4px;
  }

  :deep(.v-input:not(.v-select)) .v-field {
    border-radius: 0 4px 4px 0;

    &:not(.v-field--focused) .v-field__outline__start {
      border-inline-start-width: 0;
    }
  }
}

.v-list-item--rounded {
  border-radius: 0;

  :deep(.v-list-item__spacer) {
    width: 12px;
  }
}

fieldset {
  border: 0;
}

.v-input--density-comfortable {
  --v-input-control-height: 36px;
}
</style>
