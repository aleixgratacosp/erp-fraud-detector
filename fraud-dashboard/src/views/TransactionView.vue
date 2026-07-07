<template>
  <div class="detailContainer">
    <div>
      <Button icon="pi pi-arrow-left" label="Back to Dashboard" @click="goBack" />
      <h1>Transaction Viewer</h1>
    </div>

    <div class="inspectorGrid">

      <Card>
        <template #title>
          <div class="cardTitle">AI Risk Score</div>
        </template>
        <template #content>
          <div class="scoreContainer">
            <span class="value criticalText">{{ transaction.final_risk_score }} %</span>
          </div>
        </template>
      </Card>

      <Card>
        <template #title>
          <div class="cardTitle"> Metadata</div>
        </template>

        <template #content>
          <div class="dataGridTwoCols">
            <div class="dataRow">
              <span class="label">Transaction ID:</span>
              <span class="value monospace">{{ transaction.transaction_id }}</span>
            </div>
            <div class="dataRow">
              <span class="label">Created by:</span>
              <span class="value monospace">{{ transaction.user_id }}</span>
            </div>
            <div class="dataRow">
              <span class="label">Sold-to:</span>
              <span class="value monospace">{{ transaction.customer_id }}</span>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #title>
          <div class="cardTitle"> Financials </div>
        </template>
        <template #content>
          <div class="dataGridTwoCols">
            <div class="dataRow">
              <span class="label">Total Gross Amount:</span>
              <span class="value" style="font-size: 1.2rem;">{{ transaction.total_amount }} €</span>
            </div>
            <div class="dataRow">
              <span class="label">Applied Discount:</span>
              <span class="value">{{ transaction.discount_percent }} %</span>
            </div>
            <div class="dataRow">
              <span class="label">Product Category:</span>
              <span class="value">{{ transaction.product_category }}</span>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #title>
          <div class="cardTitle">Status</div>
        </template>
        <template #content>
          <div class="dataGridTwoCols">
            <div class="dataRow">
              <span class="label">O2C status:</span>
              <span class="value" style="font-weight: bold;">{{ transaction.order_status }}</span>
            </div>
            <div class="dataRow">
              <span class="label">Order Timestamp:</span>
              <span class="value" style="font-size: 0.95rem;">{{ transaction.timestamp_order }}</span>
            </div>
            <div class="dataRow">
              <span class="label">Shipping Date:</span>
              <span class="value" style="font-size: 0.95rem;">{{ transaction.shipping_date || 'N/A' }}</span>
            </div>
            <div class="dataRow">
              <span class="label">Invoice Release Date:</span>
              <span class="value" style="font-size: 0.95rem;">{{ transaction.invoice_date || 'N/A' }}</span>
            </div>
          </div>
        </template>
      </Card>

    </div>
  </div>
</template>

<script>
import Button from 'primevue/button';
import Card from 'primevue/card';

export default {
  name: 'TransactionView',
  components: {
    Button,
    Card
  },
  props: {
    detectionResults: Object,
    phases: Object
  },
  computed: {
    transaction() {
      if (this.detectionResults && this.detectionResults.ensemble) {
        return this.detectionResults.ensemble.find(
          item => String(item.transaction_id) === String(this.$route.params.id)
        ) || {}; 
      }
      return {};
    }
  },
  methods: {
    goBack() {
      this.$router.push('/audit');
    }
  }
}
</script>

<style scoped>
.detailContainer {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.inspectorGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.cardTitle {
  font-size: 1.1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
}

.scoreContainer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 20px 0;
  text-align: center;
}

.dataGridTwoCols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.dataRow {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px dashed var(--p-surface-border);
}

.label {
  font-size: 0.85rem;
  color: var(--p-text-muted-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  font-size: 1.05rem;
  font-weight: 600;
}

.monospace {
  font-family: 'Consolas';
  font-size: 0.95rem;
}

.criticalText {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--p-red-500);
}
</style>