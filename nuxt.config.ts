export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://ironman.antonio-ling.com',
    },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'zh-Hant' },
      link: [
        // 卡片要等這份資料才畫得出來，讓它跟 JS 同時下載
        { rel: 'preload', href: '/data/ironman.json', as: 'fetch', crossorigin: 'anonymous' },
        { rel: 'preload', href: '/fonts/wenkai-brand.woff2', as: 'font', type: 'font/woff2', crossorigin: 'anonymous' },
      ],
    },
  },
})
