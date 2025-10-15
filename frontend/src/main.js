import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ganttastic from '@infectoone/vue-ganttastic'
import '@infectoone/vue-ganttastic'

const app = createApp(App)
app.use(router)
app.use(ganttastic)
app.mount('#app')


