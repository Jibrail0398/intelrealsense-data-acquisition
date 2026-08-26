import { defineStore } from 'pinia'
import { datasetService } from '@/services/datasetService'
import { socket } from '@/services/websocket/socket'
import { useToastStore } from './toastStore'

export const useDatasetStore = defineStore('dataset', {
  state: () => ({
    datasets: [] as { id: string; name: string }[],
    labels: [] as { id: string; name: string; datasetId: string }[],
    selectedDatasetId: null as string | null,
    selectedLabelId: null as string | null,
    statistics: null as { labelName: string; count: number }[] | null,
    totalCaptures: 0,
    loadingDatasets: false,
    loadingLabels: false,
    loadingStatistics: false,
    creatingLabel: false,
    initialized: false,
  }),

  getters: {
    selectedDataset: (s) => s.datasets.find((d) => d.id === s.selectedDatasetId) ?? null,
    selectedLabel: (s) => s.labels.find((l) => l.id === s.selectedLabelId) ?? null,
    activeLabelCount(): number {
      return (
        this.statistics?.find(
          (c) =>
            c.labelName.toLowerCase().replace(/\s+/g, '') ===
            (this.selectedLabel?.name.toLowerCase().replace(/\s+/g, '') ?? ''),
        )?.count ?? 0
      )
    },
  },

  actions: {
    init() {
      if (this.initialized) return
      this.initialized = true
      socket.on('dataset.updated', () => {
        if (this.selectedDatasetId) void this.refreshStatistics(this.selectedDatasetId)
      })
      void this.loadDatasets()
    },

    async loadDatasets() {
      this.loadingDatasets = true
      try {
        this.datasets = await datasetService.getDatasets()
      } catch {
        useToastStore().error('Failed to load datasets.')
      } finally {
        this.loadingDatasets = false
      }
    },

    async selectDataset(id: string) {
      if (id === this.selectedDatasetId) return
      this.selectedDatasetId = id
      this.selectedLabelId = null
      this.statistics = null
      await this.loadLabels(id)
    },

    async loadLabels(datasetId: string) {
      this.loadingLabels = true
      try {
        this.labels = await datasetService.getLabels(datasetId)
        if (this.labels.length > 0) {
          await this.selectLabel(this.labels[0]!.id)
        }
      } catch {
        useToastStore().error('Failed to load labels.')
      } finally {
        this.loadingLabels = false
      }
    },

    selectLabel(id: string) {
      this.selectedLabelId = id
      return Promise.resolve()
    },

    async createLabel(name: string) {
      const toast = useToastStore()
      const trimmed = name.trim()
      if (!trimmed || !this.selectedDatasetId) return
      if (
        this.labels.some(
          (l) => l.name.toLowerCase() === trimmed.toLowerCase(),
        )
      ) {
        toast.warning(`Label "${trimmed}" already exists.`)
        return
      }
      this.creatingLabel = true
      try {
        const label = await datasetService.createLabel(this.selectedDatasetId, trimmed)
        this.labels.push(label)
        this.selectedLabelId = label.id
        toast.success(`Label "${trimmed}" created.`)
      } catch {
        toast.error('Failed to create label.')
      } finally {
        this.creatingLabel = false
      }
    },

    async refreshStatistics(datasetId: string) {
      this.loadingStatistics = !!this.statistics
      try {
        const stats = await datasetService.getStatistics(datasetId)
        this.statistics = stats.counts.map((c) => ({
          labelName: c.labelName,
          count: c.count,
        }))
        this.totalCaptures = stats.total
      } catch {
        useToastStore().error('Failed to load dataset statistics.')
      } finally {
        this.loadingStatistics = false
      }
    },
  },
})
