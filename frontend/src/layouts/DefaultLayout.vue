<script setup>
import { reactive } from 'vue'
import Header from '@/components/layout/header/Header.vue'
import Footer from '@/components/layout/Footer.vue'

const headerstyle = reactive({
  height: 'auto' // adjust as needed
})
</script>

<template>
  <el-container>
    <el-header :style="headerstyle">
      <Header />
    </el-header>
  </el-container>
  <el-main>
    <slot />
  </el-main>
  <Footer />
</template>
