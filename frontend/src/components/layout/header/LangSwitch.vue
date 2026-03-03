<template>
  <div class="locale-changer">
    <el-select v-model="locale">
      <el-option value="en">en</el-option>
      <el-option value="sv">sv</el-option>
    </el-select>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

</script>

<style scoped>
  .locale-changer {
    padding-right: 10px;
    margin-left: auto;
    min-width: 80px;
  }
</style>
