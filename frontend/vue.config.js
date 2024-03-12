const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  productionSourceMap: false,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // Replace with your FastAPI backend URL
        changeOrigin: true,
        pathRewrite: {'^/api': '',} // Remove the '/api' prefix when forwarding requests
      },
    }
  },

  pluginOptions: {
    i18n: {
      locale: 'sv',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: true,
    },
  },

  transpileDependencies: true
})
