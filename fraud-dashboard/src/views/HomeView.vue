<template>

    <div class="home">
        <h1>Audit Simulation Platform</h1>
        <p style="padding-bottom: 30px">Follow the following steps to replicate the whole flow.</p>

        <div class="timelineContainer">
            <ScrollPanel class="scrollPanel" :dt="{ bar: { background: '{primary.color}' } }">
                <!-- used for scroll bar-->

                <Timeline :value="timelineData" align="alternate" class="responsiveTimeline">

                    <template #marker="slotProps">
                        <span class="timelineImages" :style="getMarkerStyle(slotProps.item)">
                            <i :class="getMarkerIcon(slotProps.item)"></i>
                        </span>
                    </template>

                    <template #content="slotProps">

                        <Card>
                            <template #title>
                                {{ slotProps.item.status }}
                            </template>
                            <template #content>
                                <p>
                                    {{ slotProps.item.description }}
                                </p>
                                <Button size="small" :label="getButtonLabel(slotProps.item)"
                                    :disabled="!isPhaseAccessible(slotProps.item)"
                                    @click="$router.push(slotProps.item.route)" />
                            </template>
                        </Card>

                    </template>

                </Timeline>
            </ScrollPanel>
        </div>
    </div>
</template>

<script>
import Timeline from 'primevue/timeline'
import Card from 'primevue/card'
import Button from 'primevue/button';
import { ScrollPanel } from 'primevue';

export default {
    name: 'HomeView',
    components: {
        Timeline,
        Card,
        Button,
        ScrollPanel,
    },
    props: {
        phases: Object
    },
    methods: {
        isPhaseComplete(id) {
            if (this.phases) {
                switch (id) {
                    case 1:
                        return this.phases.phase1Done
                    case 2:
                        return this.phases.phase2Done;
                    case 3:
                        return this.phases.phase3Done;
                    default:
                        return false;
                }
            }
            else {
                return false;
            }
        },
        isPhaseAccessible(item) {
            if (item.id === 1) {
                return true;
            }

            if (this.phases) {
                // if 3 is unlocked, then 4 and 5 aswell
                switch (item.id) {
                    case 2:
                        return this.phases.phase1Done;
                    case 3:
                        return this.phases.phase2Done
                    case 4:
                        return this.phases.phase3Done;
                    case 5:
                        return this.phases.phase3Done;
                    default:
                        return false;
                }
            }
            else {
                return false
            }
        },
        getMarkerStyle(item) {
            if (this.isPhaseComplete(item.id)) {
                return {
                    backgroundColor: 'var(--p-green-500)'
                }
            }
            else {
                return {
                    backgroundColor: item.color
                }
            }

        },

        getMarkerIcon(item) {
            if (this.isPhaseComplete(item.id)) {
                return 'pi pi-check';
            }
            else {
                return item.icon;
            }

        },

        getButtonLabel(item) {
            if (this.isPhaseComplete(item.id)) {
                return 'Review';
            }
            if (!this.isPhaseAccessible(item)) {
                return 'Locked';
            }
            else {
                return 'Goto'
            }

        }
    },
    data() {
        return {
            timelineData: [
                {
                    id: 1,
                    status: '1. ERP Base Logs Generation',
                    description: 'Simulate legal transactional data from an ERP system.',
                    icon: 'pi pi-database',
                    color: 'var(--p-primary-color)',
                    route: '/generator'
                },
                {
                    id: 2,
                    status: '2. Fraud Injection',
                    description: 'Inject up to 6 different types of fraudulent transactions.',
                    icon: 'pi pi-exclamation-triangle',
                    color: 'var(--p-orange-500)',
                    route: '/injector'
                },
                {
                    id: 3,
                    status: '3. ML Detection',
                    description: 'Execute Isolation Forest,Local Outlier Factor or Ensemble to detect fraud.',
                    icon: 'pi pi-shield',
                    color: 'var(--p-red-500)',
                    route: '/detection'
                },
                {
                    id: 4,
                    status: '4. Auditing View and Detection Results',
                    description: 'Simulate how the auditor could manage these results.',
                    icon: 'pi pi-eye',
                    color: 'var(--p-blue-500)',
                    route: '/alerts',
                },
                {
                    id: 5,
                    status: '5. Graphs and Summary',
                    description: 'View the final performance metrics for your selection.',
                    icon: 'pi pi-chart-bar',
                    color: 'var(--p-pink-500)',
                    route: '/graphs'
                }
            ]
        };
    }
};
</script>

<style scoped>
.home {
    text-align: center;
}

.timelineImages {
    display: flex;
    width: 2.5rem;
    height: 2.5rem;
    align-items: center;
    justify-content: center;
    color: white;
    border-radius: 50%;
}

.timelineContainer {
    max-width: 850px;
    margin: 0 auto;
    text-align: left;
}

.scrollPanel {
    width: 100%;
    max-height: 75vh; 
    height: auto;

}
.responsiveTimeline {
    padding: 0 20px;
}

</style>