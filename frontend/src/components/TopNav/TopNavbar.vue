<template>
  <div>
    <div
      v-if="$route.params.toolVersion==='sv'"
      class="navbar-container swedish-version"
    >
      <el-menu
        :default-active="activeLink"
        background-color="#F4DE48"
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
          <span>
            Export
          </span>
        </el-menu-item>
        <el-menu-item>
          <a href="..">
            <el-button type="plain" @click="downloadManual">{{ $t('homePage.downloadManual') }}
              <i class="el-icon-collection" />
            </el-button>
          </a>
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
          <span>
            Export
          </span>
        </el-menu-item>
        <el-menu-item>
          <a href="..">
            <el-button type="plain" @click="downloadManual">{{ $t('homePage.downloadManual') }}
              <i class="el-icon-collection" />
            </el-button>
          </a>
        </el-menu-item>
      </el-menu>
      <lang-switch />
    </div>
  </div>
</template>

<script>
import LangSwitch from './LangSwitch.vue';

export default {
  components: {
    LangSwitch,
  },
  data() {
    return {
      // create activeLink to make it synchronized with chosen el-menu-item in el-menu
      activeLink: null,
    };
  },
  watch: {
    $route() {
      this.activeLink = this.$route.path;
    },
  },
  mounted() {
    this.activeLink = this.$route.path;
  },
  methods: {
    downloadManual() {
      // Open the PDF in a new tab
      window.open('/assets/swegram2-manual.pdf', '_blank');

      // Alternatively, if you want it to download directly:
      // const link = document.createElement('a');
      // link.href = '/assets/swegram2-manual.pdf';
      // link.download = 'swegram2-manual.pdf';
      // link.click();
    },
  },
};
</script>

<style scoped>

.swedish-version {
  background-color: rgb(244, 222, 72);
}

.english-version {
  background-color: rgb(242, 87, 95);
}

.navbar-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
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
