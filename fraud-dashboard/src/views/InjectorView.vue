<template>
    <div class="detectionView">
        <h1> Step 2: Fraud Injection </h1>
        <p> Inject 6 types of fraudulent scenarios into the base ERP transactions. </p>
        
        <div class="formContainer">

            <div class="formGroup">
                <label>Ghost Sales:</label>
                <InputText type="text" v-model="num_ghost" />
            </div>

            <div class="formGroup">
                <label>Channel Stuffing:</label>
                <InputText type="text" v-model="num_chstuff" />
            </div>

            <div class="formGroup">
                <label>Discount Manipulation:</label>
                <InputText type="text" v-model="num_discounts" />
            </div>

            <div class="formGroup">
                <label>Unusual Hours:</label>
                <InputText type="text" v-model="num_unusualh" />
            </div>
            
            <div class="formGroup">
                <label>Invoice Splitting:</label>
                <InputText type="text" v-model="num_splitting" />
                <i style="font-size: 13px;" > Note that this type of fraud generates ~3 times its specified amount. </i>
            </div>

            <div class="formGroup">
                <label>Premature Invoicing:</label>
                <InputText type="text" v-model="num_prematureinv" />
            </div>
        </div>

        <div style="padding-top: 30px;">
            <Button style="margin: 10px" label="Inject Frauds" @click="informofInjection" />
        </div>

        <div v-if="phase2Message" style="padding-top: 40px; max-width: 500px; margin: 0 auto; text-align: left;">
            <Card>
                <template #title>Response from server</template>
                <template #content>
                    <p style="font-family: consolas; margin: 10;">
                        {{ phase2Message }}
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
    name: "InjectorView",
    components: {
        Button,
        Card,
        InputText
    },
    props: {
        phases: Object,
        phase2Message: String
    },
    data() {
        return {
          //default values, will roughly translate to 2,35% contamination.
            num_ghost: 392,
            num_chstuff: 392,
            num_discounts: 392,
            num_unusualh: 392,
            num_splitting: 130,
            num_prematureinv: 392
        }
    },
    methods: {
        informofInjection() {
            fetch("http://127.0.0.1:5000/api/phase2/inject", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    num_ghost: parseInt(this.num_ghost),
                    num_chstuff: parseInt(this.num_chstuff),
                    num_discounts: parseInt(this.num_discounts),
                    num_unusualh: parseInt(this.num_unusualh),
                    num_splitting: parseInt(this.num_splitting),
                    num_prematureinv: parseInt(this.num_prematureinv)
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        this.$emit("changePhase", { phase: 2, value: true, message: data.message })
                    } 
                    else {
                        this.$emit("changePhase", { phase: 2, value: false, message: "Error: " + data.message });
                    }
                })
                .catch(error => {
                    this.$emit("changePhase", { phase: 2, value: false, message: "Error: " + error.message });
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
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    max-width: 600px;
    margin: 40px auto 0 auto;
    text-align: left;
}

.formGroup {
    display: flex;
    flex-direction: column;
}

.formGroup label {
    font-weight: bold;
    font-size: 0.9rem;
}
</style>