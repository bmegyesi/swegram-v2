import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import VueCookies from 'vue3-cookies'

import 'element-plus/dist/index.css'
import '@/assets/styles/main.css'

const app = createApp(App)

app.use(router)
app.use(VueCookies)
app.use(i18n)

app.mount('#app')
