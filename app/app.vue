<script setup lang="ts">
const config = useRuntimeConfig()

const siteName = 'iThome 鐵人賽作品查詢'
const pageTitle = 'iThome 鐵人賽作品查詢｜2022–2026 系列、團隊與得獎名單'
const description = '查 iThome 鐵人賽 2022–2026 的參賽系列與團隊，得獎作品排在前面。可搜尋系列、每日文章標題與作者，先看每天寫什麼再決定是否點進去；點作者可查看他歷年的所有作品。'
const siteUrl = String(config.public.siteUrl).replace(/\/$/, '')
const ogImageUrl = `${siteUrl}/og.png`

useSeoMeta({
  title: pageTitle,
  description,
  ogTitle: siteName,
  ogDescription: description,
  ogUrl: siteUrl,
  ogImage: ogImageUrl,
  ogType: 'website',
  ogLocale: 'zh_TW',
  twitterCard: 'summary_large_image',
  twitterTitle: siteName,
  twitterDescription: description,
  twitterImage: ogImageUrl,
})

useHead({
  link: [
    { rel: 'canonical', href: siteUrl },
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
  ],
  meta: [
    { name: 'theme-color', content: '#fbfcfd', media: '(prefers-color-scheme: light)' },
    { name: 'theme-color', content: '#0e1626', media: '(prefers-color-scheme: dark)' },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: siteName,
        url: siteUrl,
        inLanguage: 'zh-Hant',
      }),
    },
  ],
})
</script>

<template>
  <NuxtPage />
</template>
