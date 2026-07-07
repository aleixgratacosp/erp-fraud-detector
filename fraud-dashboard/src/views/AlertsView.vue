<template>
  <div style="padding: 2rem;">

    <h1>ERP Fraud Dashboard</h1>
    <p>Review the anomalies detected by the unsupervised Machine Learning models.</p>

    <div style="margin-top: 25px; margin-bottom: 25px;">

      <Button label="Open Auditor Simulator" icon="pi pi-eye" class="p-button-help" :disabled="!isEnsembleAvailable"
        @click="goToAuditorSimulator" />

      <i v-if="!isEnsembleAvailable" style="font-size: 12px">
        * Requires Ensemble model results to unlock the auditor simulator view.
      </i>

    </div>

    <div v-if="hasResults" style="margin-top: 20px;">
      <Tabs value="0">
        <TabList>

          <Tab value="0">Ensemble ({{ safeResults.ensemble.length }})</Tab>
          <Tab value="1">Isolation Forest ({{ safeResults.iforest.length }})</Tab>
          <Tab value="2">LOF ({{ safeResults.lof.length }})</Tab>

        </TabList>

        <TabPanels style="padding-top: 15px;">

          <TabPanel value="0">
            <DataTable :value="safeResults.ensemble" paginator :rows="10" stripedRows size="small"
              responsiveLayout="scroll">

              <Column field="final_risk_score" header="Risk Score (%)" sortable></Column>
              <Column field="transaction_id" header="ID" sortable></Column>
              <Column field="customer_id" header="Customer" sortable></Column>
              <Column field="total_amount" header="Amount (€)" sortable></Column>
              <Column field="timestamp_order" header="Date" sortable></Column>
              <Column field="order_status" header="Status" sortable></Column>

            </DataTable>
          </TabPanel>

          <TabPanel value="1">
            <DataTable :value="safeResults.iforest" paginator :rows="10" stripedRows size="small"
              responsiveLayout="scroll">

              <Column field="final_risk_score" header="iForest Score (%)" sortable></Column>
              <Column field="transaction_id" header="ID" sortable></Column>
              <Column field="customer_id" header="Customer" sortable></Column>
              <Column field="product_category" header="Category" sortable></Column>
              <Column field="total_amount" header="Amount (€)" sortable></Column>

            </DataTable>

          </TabPanel>

          <TabPanel value="2">
            <DataTable :value="safeResults.lof" paginator :rows="10" stripedRows size="small" responsiveLayout="scroll">

              <Column field="final_risk_score" header="LOF Score (%)" sortable></Column>
              <Column field="transaction_id" header="ID" sortable></Column>
              <Column field="customer_id" header="Customer" sortable></Column>
              <Column field="total_amount" header="Amount (€)" sortable></Column>
              <Column field="order_status" header="Status" sortable></Column>

            </DataTable>

          </TabPanel>

        </TabPanels>
      </Tabs>
    </div>
  </div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'

export default {
  name: 'FraudDashboard',
  components: {
    DataTable,
    Column,
    Tabs,
    TabList,
    Tab,
    TabPanels,
    TabPanel,
    Button
  },
  props: {
    phases: Object,
    detectionResults: Object
  },
  computed: {
    safeResults() {
      let results = {
        ensemble: [],
        iforest: [],
        lof: []
      };
      if (this.detectionResults) {

        if (this.detectionResults.ensemble) {
          results.ensemble = this.detectionResults.ensemble;
        }

        if (this.detectionResults.iforest) {
          results.iforest = this.detectionResults.iforest;
        }

        if (this.detectionResults.lof) {
          results.lof = this.detectionResults.lof;
        }
      }

      return results;
    },
    hasResults() {
      return (this.safeResults.ensemble.length > 0 || this.safeResults.iforest.length > 0 || this.safeResults.lof.length > 0);
    },
    isEnsembleAvailable() {
      return (this.safeResults.ensemble.length > 0)
    }
  },
  methods: {
    goToAuditorSimulator() {
      this.$router.push("/audit");
    }
  }
}
</script>

<style scoped></style>