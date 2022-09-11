<template>
  <div class="locale-changer">
    <el-select v-model="$i18n.locale">
      <el-option
        v-for="(lang, i) in langs"
        :key="`Lang${i}`"
        :value="lang"
      >
        {{ lang }}
      </el-option>
    </el-select>
  </div>
</template>

<script>
export default {
  name: 'LocaleChanger',
  data() {
    return { langs: ['sv', 'en'] };
  },
};
</script>

<style scoped>
  .locale-changer {
    padding-right: 10px;
  }
</style>
