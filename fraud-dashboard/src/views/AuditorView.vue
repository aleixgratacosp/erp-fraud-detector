<template>
  <div class="auditorContainer">
    <h1 style="text-align: center;">Step 4: Auditor Simulation Dashboard</h1>

    <div class="statsGrid">

      <Card>
        <template #title>Total Alerts</template>
        <template #content>
          <div class="statNumber" style="color: var(--p-blue-500);">{{ safeEnsemble.length }}</div>
        </template>
      </Card>

      <!-- the number on this card lowers when selected-->
      <Card>
        <template #title>Reviews Pending</template>
        <template #content>
          <div class="statNumber" style="color: var(--p-red-500);">{{ criticalCount }}</div>
        </template>
      </Card>

      <Card>
        <template #title>Total Amount at Risk</template>
        <template #content>
          <div class="statNumber" style="color: var(--p-purple-500);">{{ totalRiskAmount }} €</div>
        </template>
      </Card>
    </div>

    <div class="tableContainer">
      <DataTable :value="safeEnsemble" paginator :rows="10" stripedRows size="small" responsiveLayout="scroll"
        sortField="final_risk_score" :sortOrder="-1">

        <Column field="final_risk_score" header="Risk Score" sortable>

          <template #body="slotProps">
            <div style="display: flex; align-items: center; gap: 8px;">

              <Button icon="pi pi-eye" @click="viewTransactionDetails(slotProps.data)"
                style="padding: 0; width: 24px; height: 24px;" />

              <span>
                {{ slotProps.data.final_risk_score }} %
              </span>
            </div>
          </template>
        </Column>

        <Column field="transaction_id" header="Transaction ID" sortable></Column>
        <Column field="customer_id" header="Customer" sortable></Column>
        <Column field="product_category" header="Category" sortable></Column>
        <Column field="total_amount" header="Amount" sortable>

          <template #body="slotProps">
            {{ slotProps.data.total_amount }} €
          </template>

        </Column>

        <Column field="timestamp_order" header="Order Date" sortable></Column>
        <Column field="order_status" header="ERP Status"></Column>

        <Column header="Audit Decision">
          <template #body="slotProps">

            <!-- auditeditems: stores what decision we have taken-->
            <!-- if we have taken a decision-->
            <div v-if="auditedItems[slotProps.data.transaction_id]" style="display: flex; align-items: center; ">
              <span>
                <!-- (show selected label)-->
                {{ auditedItems[slotProps.data.transaction_id].label }}
              </span>

              <Button icon="pi pi-refresh" @click="resetDecision(slotProps.data.transaction_id)"
                style="margin-left: auto;" />
            </div>

            <!-- else we show the two buttons-->
            <div v-else style="display: flex; gap: 8px;">
              <Button label="Dismiss" style="background-color: var(--p-blue-500);"
                @click="setDecision(slotProps.data.transaction_id, 'Legitimate')" />

              <Button label="Fraud" style="background-color: var(--p-red-500);"
                @click="setDecision(slotProps.data.transaction_id, 'Fraud')" />
            </div>
          </template>
        </Column>

      </DataTable>
    </div>
  </div>
</template>

<script>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Card from 'primevue/card';
export default {
  name: 'AuditorView',
  components: {
    DataTable,
    Column,
    Button,
    Card
  },
  props: {
    phases: Object,
    detectionResults: Object,
    auditedItems: Object,
  },
  data() {
    return {
    };
  },
  computed: {
    safeEnsemble() {
      if (this.detectionResults && this.detectionResults.ensemble) {
        return this.detectionResults.ensemble;
      }
      else {
        return [];
      }
    },

    criticalCount() {
      let count = 0;
      let list = this.safeEnsemble;

      for (let i = 0; i < list.length; i++) {
        let item = list[i];
        let isReviewed = this.auditedItems[item.transaction_id] !== undefined;

        if (!isReviewed) {
          count = count + 1;
        }
      }
      return count;
    },

    totalRiskAmount() {
      let total = 0;
      let list = this.safeEnsemble;

      for (let i = 0; i < list.length; i++) {
        let item = list[i];
        let amount = parseFloat(item.total_amount);

        if (!isNaN(amount)) {
          total = total + amount;
        }
      }
      //so we get in euros
      return total.toLocaleString("es-ES", { minimumFractionDigits: 2 });
    }

  },
  methods: {
    viewTransactionDetails(transaction) {
      this.$router.push(`/transaction/${transaction.transaction_id}`);
    },

    setDecision(transactionId, label) {
      this.$emit('updateAudited', {
        type: 'set',
        id: transactionId,
        value: { label: label }
      });
    },
    resetDecision(transactionId) {
      this.$emit('updateAudited', {
        type: 'reset',
        id: transactionId
      });
    },
  }
}
</script>

<style scoped>
.auditorContainer>p {
  text-align: center;
  color: var(--p-text-muted-color);
  margin-bottom: 2rem;
}

.statsGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto 30px auto;
}

.statNumber {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.tableContainer {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--p-surface-card);
  border-radius: 6px;
  border: 1px solid var(--p-surface-border);
  padding: 10px;
}

.subtitleCard {
  font-size: 12px;
}
</style>
