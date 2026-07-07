<template>
    <div class="detectionView">
        <h1> Step 1: ERP Base logs </h1>
        <p> Specify the amount of legal transactions you want to create. </p>
        
        <div style="padding-top: 50px;">
            <InputText type="text" v-model="value" />
            <Button style="margin: 10px" label="Generate Logs" @click="informofGeneration" />
        </div>
        <!-- messages from backend-->
        <div v-if="phase1Message" style="padding-top: 70px; max-width: 500px; margin: 0 auto; text-align: left;">
            <Card>
                <template #title>Response from server</template>
                <template #content>
                    <p style="font-family: consolas; margin: 10px;">
                        {{ phase1Message }}
                    </p>
                </template>
            </Card>
        </div>
    </div>
</template>

<script>
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Card from 'primevue/card';

export default {
    name: 'GeneratorView',
    components: {
        Button,
        InputText,
        Card,
    },
    data() {
        return {
            value: 100000
        }
    },
    props: {
        phases: Object,
        phase1Message: String
    },
    methods: {
        // sends info to parent and to backend.then retrieves it
        informofGeneration() {
            fetch('http://127.0.0.1:5000/api/phase1/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: parseInt(this.value)
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.$emit('changePhase', { phase: 1, value: true, message: data.message });
                    } 
                    else {
                        this.$emit('changePhase', { phase: 1, value: false, message: 'Error: ' + data.message });
                    }
                })
                .catch(error => {
                    this.$emit('changePhase', { phase: 1, value: false, message: 'Error: ' + error.message });
                });
        }
    }
}
</script>

<style scoped>
.detectionView {
    text-align: center;
}
</style>