<script setup>
import { ref, watch, onMounted } from 'vue';
import LangSwitch from './LangSwitch.vue';
import { useRoute } from 'vue-router';

const activeLink = ref(null);
const route = useRoute();
let currentVersion = route.params.toolVersion

watch(() => route.params.toolVersion, (newVersion) => {
  currentVersion = newVersion
})

watch(() => route.path, (newPath) => {
  activeLink.value = newPath;
});

onMounted(() => {
  activeLink.value = route.path;
});

function downloadManual() {
  // Open the PDF in a new tab
  window.open('/assets/swegram2-manual.pdf', '_blank');

  // Alternative direct download (commented)
  // const link = document.createElement('a');
  // link.href = '/assets/swegram2-manual.pdf';
  // link.download = 'swegram2-manual.pdf';
  // link.click();
}
</script>

<template>
  <div>
    <div
      v-if="currentVersion==='sv'"
      class="navbar-container swedish-version"
    >
      <el-menu
        :default-active="activeLink"
        class="el-menu"
        active-text-color="black"
        mode="horizontal"
        router
      >
        <el-menu-item index="/sv">
          {{ $t('topNavbar.home') }}
        </el-menu-item>
        <el-menu-item index="/sv/upload">
          {{ $t('topNavbar.addText') }}
        </el-menu-item>
        <el-menu-item index="/sv/visualize">
          {{ $t('topNavbar.visualize') }}
        </el-menu-item>
        <el-menu-item index="/sv/statistics">
          {{ $t('topNavbar.statistics') }}
        </el-menu-item>
        <el-menu-item index="/sv/export">
          {{ $t('topNavbar.export') }}
        </el-menu-item>
        <el-menu-item index="download-manual" @click="downloadManual">
          {{ $t('homePage.downloadManual') }}
        </el-menu-item>
      </el-menu>
      <lang-switch />
    </div>
    <div
      v-if="$route.params.toolVersion==='en'"
      class="navbar-container english-version"
    >
      <el-menu
        :default-active="activeLink"
        background-color="#F2575F"
        active-text-color="black"
        mode="horizontal"
        router
      >
        <el-menu-item index="/en">
          {{ $t('topNavbar.home') }}
        </el-menu-item>
        <el-menu-item index="/en/upload">
          {{ $t('topNavbar.addText') }}
        </el-menu-item>
        <el-menu-item index="/en/visualize">
          {{ $t('topNavbar.visualize') }}
        </el-menu-item>
        <el-menu-item index="/en/statistics">
          {{ $t('topNavbar.statistics') }}
        </el-menu-item>
        <el-menu-item index="/en/export">
          {{ $t('topNavbar.export') }}
        </el-menu-item>
        <el-menu-item index="download-manual" @click="downloadManual">
          {{ $t('homePage.downloadManual') }}
        </el-menu-item>
      </el-menu>
      <lang-switch />
    </div>
  </div>
</template>

<style scoped>

.swedish-version {
  background-color: rgb(244, 222, 72);
}

.english-version {
  background-color: rgb(242, 87, 95);
}

.navbar-container {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.el-menu {
  background-color: #F4DE48;
  flex-grow: 1;
}

.hyperlink {
  text-decoration: none;
  color: #303133;
}

.el-menu.el-menu--horizontal {
  border-bottom: none;
}

.el-menu-item a {
  vertical-align: baseline;
}
</style>
