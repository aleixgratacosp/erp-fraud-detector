import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import GeneratorView from './views/GeneratorView.vue' 
import InjectorView from './views/InjectorView.vue'   
import DetectionView from './views/DetectionView.vue'  
import AlertsView from './views/AlertsView.vue'       
import GraphicsView from './views/GraphicsView.vue'   
import AuditorView from './views/AuditorView.vue'
import TransactionView from './views/TransactionView.vue'

const routes = [
  { path: '/', component: HomeView }, 
  { path: '/generator', component: GeneratorView }, 
  { path: '/injector', component: InjectorView },   
  { path: '/detection', component: DetectionView }, 
  { path: '/alerts', component: AlertsView },  
  { path: '/graphs', component: GraphicsView },
  { path: '/audit', component: AuditorView},
  { path: '/transaction/:id', component: TransactionView }

]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router