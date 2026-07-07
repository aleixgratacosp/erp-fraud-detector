<template>
  <Menubar :model="items" style="padding-right: 100px;">
    <template #start>
      <span style="font-weight: bold; font-size: 1.2rem; color: var(--p-primary-color);">
        Fraud Simulator ERP
      </span>
    </template>
  </Menubar>

  <div>
    <!-- In the web, only the message of the execution itself is saved. The actual info comes from the .csv files-->
    <router-view :phases="phases" :phase1-message="phase1Message" :phase2-message="phase2Message"
      :phase3-message="phase3Message" :detection-results="detectionResults" :audited-items="auditedItems"
      @changePhase="updatePhase" @updateAudited="updateAuditedItems">
    </router-view>
  </div>
</template>

<script>

import Menubar from "primevue/menubar"

export default {
  components: {
    Menubar
  },
  data() {
    return {
      items: [
        {
          label: "Home",
          icon: "pi pi-home",
          command: () => {
            this.$router.push("/")
          }
        }
      ],

      phases: {
        phase1Done: false,
        phase2Done: false,
        phase3Done: false
      },
      phase1Message: "No dataset generated yet",
      phase2Message: "No fraud injected yet",
      phase3Message: "No detection executed yet",

      detectionResults: {
        ensemble: [],
        iforest: [],
        lof: []
      },
      auditedItems: {}
    }
  },
  methods: {
    updatePhase(data) {
      if (data.phase === 1) {
        this.phases.phase1Done = data.value;
        this.phase1Message = data.message;
      }
      if (data.phase === 2) {
        this.phases.phase2Done = data.value;
        this.phase2Message = data.message;
      }
      if (data.phase === 3) {
        this.phases.phase3Done = data.value;
        this.detectionResults = data.results;
        this.phase3Message = data.message;
      }
    },
    updateAuditedItems(payload) {
      if (payload.type === 'set') {
        this.auditedItems[payload.id] = payload.value;
      } 
      else if (payload.type === 'reset') {
        delete this.auditedItems[payload.id];
      }
    },
  }
}
</script>


<style>
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: "Inter";
  background-color: var(--p-surface-50);
  color: var(--p-text-color);
}

div {
  margin: 0;
  padding: 0;
}
</style>