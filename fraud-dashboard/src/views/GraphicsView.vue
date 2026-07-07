<template>
  <div class="metricsView">
    <h1>Step 5: Model Performance Graphs</h1>

    <div class="dashboardGrid">

      <template v-for="(data, algoName) in metrics" :key="algoName">
        <Card v-if="isAlgoExecuted(algoName)" style="border: 1px solid var(--p-surface-border);">

          <template #title>{{ formatAlgoName(algoName) }}</template>
          <template #content>

            <div class="dataSection">
              <h3>Performance Metrics</h3>

              <div style="margin-bottom: 10px;">
                <span class="dimLabel">Detected Transactions: <b>{{ data.tp + data.fp }}</b></span>
              </div>
              <div style="margin-bottom: 10px;">
                <span class="dimLabel">Precision: <b>{{ data.precision }}%</b></span>
                <ProgressBar :value="data.precision" :showValue="false" />
              </div>
              <div style="margin-bottom: 10px;">
                <span class="dimLabel">Recall: <b>{{ data.recall }}%</b></span>
                <ProgressBar :value="data.recall" :showValue="false" />
              </div>
            </div>

            <div class="dataSection">
              <h3>Confusion Matrix</h3>
              <div class="cmGrid">
                <div class="cmCell">True Negatives: <b>{{ data.tn }}</b></div>
                <div class="cmCell">False Positives: <b>{{ data.fp }}</b></div>
                <div class="cmCell">False Negatives: <b>{{ data.fn }}</b></div>
                <div class="cmCell">True Positives: <b>{{ data.tp }}</b></div>
              </div>
            </div>

            <div class="dataSection">
              <h3>Types of fraud</h3>
              <div style="height: 180px; position: relative;">
                <Chart type="bar" :data="getChartData(data.caught_breakdown)" :options="chartOptions"
                  style="height: 100%;" />
              </div>
            </div>

          </template>
        </Card>
      </template>
    </div>
  </div>
</template>

<script>
import Card from 'primevue/card';
import ProgressBar from 'primevue/progressbar';
import Chart from 'primevue/chart';

export default {
  name: 'GraphView',
  components: {
    Card,
    ProgressBar,
    Chart
  },
  props: {
    phases: Object,
    detectionResults: Object
  },
  data() {
    return {
      loading: true,
      metrics: {},
      // config for the graphs shown at the bottom
      chartOptions: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: 'rgba(0, 0, 0, 0.05)' },
            ticks: { font: { size: 10 } }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 10 } }
          }
        }
      }
    }
  },
  mounted() {
    this.fetchMetrics();
  },
  methods: {
    fetchMetrics() {
      fetch('http://127.0.0.1:5000/api/phase5/metrics')
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            this.metrics = data.metrics;
          }
          this.loading = false;
        })
        .catch(error => {
          console.error("error:", error);
          this.loading = false;
        });
    },
    formatAlgoName(name) {
      if (name === 'iforest') return 'Isolation Forest';
      if (name === 'lof') return 'Local Outlier Factor';
      if (name === 'ensemble') return 'Ensemble Voting Model';
      return name;
    },
    isAlgoExecuted(algoName) {
      if (!this.detectionResults || !this.detectionResults[algoName]) {
        return false;
      }
      return this.detectionResults[algoName].length > 0;
    },

    getChartData(breakdown) {
      if (!breakdown) {
        return { 
          labels: [], 
          datasets: [] 
        };
      }
      //we get a dict from backend {"Unusual Hours": 4, ...} we transform into ->  [["Unusual Hours", 4], ...]
      const sortedEntries = Object.entries(breakdown)
        //then we sort it, largest to smallest
        .sort((a, b) => b[1] - a[1]);

      const labels = sortedEntries.map(entry => entry[0]);
      const dataValues = sortedEntries.map(entry => entry[1]);

      return {
        labels: labels,
        datasets: [
          {
            data: dataValues,
            backgroundColor: 'rgba(59, 130, 246, 0.75)',
            borderRadius: 4,
            barThickness: 12
          }
        ]
      };
    }
  }
}
</script>

<style scoped>
.metricsView {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboardGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 30px;
  text-align: left;
}

.dataSection:not(:last-child) {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed var(--p-surface-border);
}

.dataSection h3 {
  font-size: 1rem;
  margin: 0 0 12px;
  color: var(--p-text-color);
}

.dimLabel {
  display: block;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.cmGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.cmCell {
  background-color: var(--p-surface-50);
  padding: 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  text-align: center;
}
</style>