import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Annotate from '../views/Annotate.vue'
import Visualize from '../views/Visualize.vue'
import Statistics from '../views/Statistics.vue'
import Export from '../views/Export.vue'

const routes = [
  {
    path: '/:toolVersion(sv|en)',
    component: Home,
  },
  {
    path: '/:toolVersion(sv|en)/upload',
    component: Annotate
  },
  {
    path: '/:toolVersion(sv|en)/visualize',
    component: Visualize
  },
  {
    path: '/:toolVersion(sv|en)/statistics',
    component: Statistics
  },
  {
    path: '/:toolVersion(sv|en)/export',
    component: Export
  },
  {
    path: "/",
    redirect: "/sv",
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
