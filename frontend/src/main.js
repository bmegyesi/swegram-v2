import Vue from 'vue';
import VueRouter from 'vue-router';
import ElementUI from 'element-ui';
import axios from 'axios';
import VueCookies from 'vue-cookies';
import 'element-ui/lib/theme-chalk/index.css';
import i18n from './i18n/i18n';

import App from './App.vue';
import HomePage from './components/HomePage.vue';
import MainPage from './components/MainPage.vue';
import UploadPage from './components/Upload/UploadPage.vue';
import HelpPage from './components/HelpPage.vue';
import DownloadPage from './components/DownloadPage.vue';
import VisualizePage from './components/Visualize/VisualizePage.vue';
import StatisticsPage from './components/Statistics/StatisticsPage.vue';

Vue.config.productionTip = false;
Vue.use(VueRouter);
Vue.use(ElementUI);
Vue.use(VueCookies);

axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';
axios.defaults.xsrfCookieName = 'csrftoken';

const router = new VueRouter({
  routes: [
    {
      path: '/:toolVersion(en|sv)',
      component: MainPage,
      children: [
        { path: '', component: HomePage },
        { path: 'upload', component: UploadPage },
        { path: 'export', component: DownloadPage },
        { path: 'help', component: HelpPage },
        {
          path: 'visualize/',
          name: 'visualize',
          component: VisualizePage,
        },
        {
          path: 'statistics/',
          name: 'statistics',
          component: StatisticsPage,
        },
      ],
    },
    {
      path: '/sv',
      props: { lang: 'sv' },
      children: [
        { path: '', component: HomePage },
        { path: '/upload', component: UploadPage },
        { path: '/export', component: DownloadPage },
        { path: '/help', component: HelpPage },
        {
          path: '/visualize/',
          name: 'visualizeSV',
          component: VisualizePage,
        },
        {
          path: '/statistics/',
          name: 'statisticsSV',
          component: StatisticsPage,
        },
      ],
    },
    {
      path: '/en',
      props: { lang: 'en' },
      children: [
        { path: '', component: HomePage },
        { path: '/upload', component: UploadPage },
        { path: '/export', component: DownloadPage },
        { path: '/help', component: HelpPage },
        {
          path: '/visualize/',
          name: 'visualizeEN', // why EN|Sv here?
          component: VisualizePage,
        },
        {
          path: '/statistics/',
          name: 'statisticsEN',
          component: StatisticsPage,
        },
      ],
    },
  ],
});

new Vue({
  router,
  i18n,
  render: (h) => h(App),
}).$mount('#app');
