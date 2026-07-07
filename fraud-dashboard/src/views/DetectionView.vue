<template>
    <div class="detectionView">
        <h1>Step 3: Machine Learning Fraud Detection</h1>
        <p>Trigger the unsupervised learning models to analyze the dataset and find anomalies.</p>

        <div class="formContainer">

            <div class="algoRow">
                <div>
                    <input type="checkbox" id="checkEnsemble" v-model="runEnsemble" />
                    <label for="checkEnsemble">Ensemble Model</label>
                </div>
                <div>
                    <label>Threshold Score (%):</label>
                    <InputText type="text" v-model="thresholdEnsemble" placeholder="99.5" />
                    <!-- Ideal beta-->
                </div>
            </div>

            <div class="algoRow">
                <div>
                    <input type="checkbox" id="checkIforest" v-model="runIforest" />
                    <label for="checkIforest">Isolation Forest</label>
                </div>
                <div>
                    <label>Contamination Rate:</label>
                    <InputText type="text" v-model="contIforest" placeholder="0.0093" />
                    <!-- Ideal beta-->
                </div>
            </div>

            <div class="algoRow">
                <div>
                    <input type="checkbox" id="checkLof" v-model="runLof" />
                    <label for="checkLof">Local Outlier Factor (LOF)</label>
                </div>
                <div>
                    <label>Contamination Rate:</label>
                    <InputText type="text" v-model="contLof" placeholder="0.0048" />
                    <!-- Ideal beta-->
                </div>
            </div>

        </div>

        <div style="padding-top: 30px;">
            <Button label="Analyze Logs with ML" :loading="loading" :disabled="!anyAlgoSelected"
                @click="executeDetections" />
        </div>

        <div v-if="phase3Message" style="padding-top: 40px; max-width: 500px; margin: 0 auto; text-align: left;">
            <Card>
                <template #title>Response from server</template>
                <template #content>
                    <p style="font-family: consolas; margin: 0; white-space: pre-line;">
                        {{ phase3Message }}
                    </p>
                </template>
            </Card>
        </div>
    </div>
</template>

<script>

import Button from "primevue/button";
import Card from "primevue/card";
import InputText from "primevue/inputtext";

export default {
    name: "DetectionView",
    components: {
        Button,
        Card,
        InputText,
    },
    props: {
        phases: Object,
        detectionResults: Object,
        phase3Message: [String, Array]
    },
    data() {
        return {
            loading: false,
            runEnsemble: true,
            runIforest: true,
            runLof: true,
            thresholdEnsemble: "99.5",
            contIforest: "0.0093",
            contLof: "0.0048"
        }
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
        
        anyAlgoSelected() {
            return (this.runEnsemble || this.runIforest || this.runLof)
        }
    },
    methods: {
        countFraud(res) {
            let count = 0;
            if (res.data) {
                let arrayData = res.data;
                for (let i = 0; i < arrayData.length; i++) {
                    let item = arrayData[i];
                    if (item.ai_is_fraud === 1) {
                        count = count + 1;
                    }
                }
            }
            return count;

        },
        getFraudList(res) {
            let filteredArray = [];
            let arrayData = res.data;

            for (let i = 0; i < arrayData.length; i++) {
                let item = arrayData[i];

                if (item.ai_is_fraud === 1) {
                    filteredArray.push(item);
                }
            }

            return filteredArray;
        },
        requestServer(algoKey, isSelected, rawValue, defaultValue, messagesArray) {
            // Returns: Promise (dont reject)
            if (!isSelected) {
                return Promise.resolve({ 
                    data: [], 
                    skipped: true 
                });
            }
            let contaminationValue = parseFloat(rawValue);
            if (isNaN(contaminationValue)) {
                contaminationValue = defaultValue;
            }


            const headers = { "Content-Type": "application/json" };
            const body = { contamination: contaminationValue }

            return fetch(`http://127.0.0.1:5000/api/phase3/detect?algo=${algoKey}`, {
                method: "POST",
                headers,
                body: JSON.stringify(body)
            })
                .then(res => res.json())
                .then(res => {
                    if (res.status === "success") {
                        const count = this.countFraud(res)

                        messagesArray.push(`${algoKey}, Found ${count} anomalies`);
                    }
                    else {
                        messagesArray.push(`${algoKey}, Error: ${res.message}`);
                    }
                    return res;
                })
                .catch(err => {
                    messagesArray.push(`${algoKey} Connection Error: ${err.message}`);
                    return { data: [], skipped: true };
                });
        },

        executeDetections() {
            this.loading = true;
            this.$emit("changePhase",
                {
                    phase: 3,
                    value: false,
                    results: this.safeResults,
                    message: "Running detection models... Wait..."
                });

            let messages = [];

            const alCalls = [
                this.requestServer("ensemble", this.runEnsemble, this.thresholdEnsemble, 99.5, messages),
                this.requestServer("iforest", this.runIforest, this.contIforest, 0.0093, messages),
                this.requestServer("lof", this.runLof, this.contLof, 0.0048, messages)
            ];

            Promise.all(alCalls)
                .then(([resEnsemble, resIforest, resLof]) => {

                    //so if user unmarks data is there
                    let listEnsemble = this.safeResults.ensemble;
                    let listIforest = this.safeResults.iforest;
                    let listLof = this.safeResults.lof;

                    if (!resEnsemble.skipped && resEnsemble.status === "success" && resEnsemble.data) {
                        listEnsemble = this.getFraudList(resEnsemble);
                    }

                    if (!resIforest.skipped && resIforest.status === "success" && resIforest.data) {
                        listIforest = this.getFraudList(resIforest);
                    }

                    if (!resLof.skipped && resLof.status === "success" && resLof.data) {
                        listLof = this.getFraudList(resLof);
                    }

                    this.$emit("changePhase", {
                        phase: 3,
                        value: true,
                        results: {
                            ensemble: listEnsemble,
                            iforest: listIforest,
                            lof: listLof
                        },
                        message: messages
                    });

                    this.loading = false;
                })
                .catch(err => {
                    this.$emit("changePhase", {
                        phase: 3,
                        value: false,
                        results: this.safeResults,
                        message: "Error: " + err.message
                    });
                    this.loading = false;
                });
        }
    }
}
</script>

<style scoped>
.detectionView {
    text-align: center;
}

.formContainer {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 600px;
    margin: 40px auto 0 auto;
    text-align: left;
}

.algoRow {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: 20px;
}

</style>