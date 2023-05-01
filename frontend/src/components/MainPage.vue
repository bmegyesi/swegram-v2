<template>
  <el-container>
    <el-header>
      <top-navbar />
    </el-header>
    <el-main>
      <router-view
        ref="mainComponent"
        @uploaded="handleFileUploaded"
      />
    </el-main>
  </el-container>
</template>

<script>
import TopNavbar from './TopNav/TopNavbar.vue';

export default {
  components: {
    TopNavbar,
  },
  methods: {
    handleFileUploaded: () => {},
  },
};
</script>
