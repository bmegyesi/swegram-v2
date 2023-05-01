<template>
  <el-container>
    <el-aside>
      <div class="icons-container">
        <img
          src="../assets/swe-clarin-logo.png"
          height="110"
          width="160"
        >
        <img
          src="../assets/UU_logo_sv_84_transparent.png"
          height="125"
          width="125"
        >
        <p class="link-container">
          <a href="..">
            <el-button type="plain">{{ $t('homePage.legacyVersion') }}
              <i class="el-icon-time" />
            </el-button>
          </a>
        </p>
        <p class="link-container">
          <a href="..">
            <el-button type="plain">{{ $t('homePage.downloadManual') }}
              <i class="el-icon-collection" />
            </el-button>
          </a>
        </p>
      </div>
    </el-aside>
    <el-container>
      <el-main>
        <div class="swegram-title">
          <h1>SWEGRAM</h1>
        </div>
        <div class="button-container">
          <router-link to="/sv/upload">
            <el-card
              shadow="never"
              class="button-wrapper"
              body-style="display: flex; flex-direction: column; align-items: center;"
            >
              <img
                src="../assets/sv.png"
                width="80px"
                height="80px"
              ><br>
              <span>{{ $t('homePage.svEntryText') }}</span>
            </el-card>
          </router-link>
          <router-link to="/en/upload">
            <el-card
              shadow="never"
              class="button-wrapper"
              body-style="display: flex; flex-direction: column; align-items: center;"
            >
              <img
                src="../assets/en.png"
                width="80px"
                height="80px"
              ><br>
              <span>{{ $t('homePage.enEntryText') }}</span>
            </el-card>
          </router-link>
        </div>
        <h2>{{ $t('homePage.about') }}</h2>
        <div class="info-container">
          <p>{{ $t('homePage.swegramIntro') }}</p>
          <i18n
            path="homePage.purpose"
            tag="p"
          >
            <a href="https://sweclarin.se">SWE-CLARIN</a>
          </i18n>
          <el-divider />
          <b>{{ $t('homePage.projectLeader') }}</b>: {{ $t('homePage.projectLeaderContent') }}<br>
          <b>{{ $t('homePage.participant') }}</b>: {{ $t('homePage.participantContent') }}<br>
          <!-- <b>{{ $t('homePage.developer') }}</b>: {{ $t('homePage.developerContent') }}<br> -->
          <el-divider />
          <b>{{ $t('homePage.references') }}</b>: <br>
          <i18n
            path="homePage.reference2019"
            :tag="false"
          >
            <a href="https://cl.lingfil.uu.se/~bea/publ/swegram-manual-2019.pdf">{{ $t('homePage.getPDF') }}</a>
          </i18n>
          <br>
          <i18n
            path="homePage.reference2017"
            :tag="false"
          >
            <a href="https://cl.lingfil.uu.se/~bea/publ/swegram-2017.pdf">{{ $t('homePage.getPDF') }}</a>
          </i18n>
        </div>
      </el-main>
      <el-footer>
        <div class="footer-container">
          <i18n
            path="homePage.iconsCredit"
            :tag="false"
          >
            <a
              href="https://www.flaticon.com/authors/madebyoliver"
              title="Madebyoliver"
            >Madebyoliver</a>
            <a
              href="http://www.flaticon.com"
              title="Flaticon"
            >www.flaticon.com</a>
            <a
              href="http://creativecommons.org/licenses/by/3.0/"
              title="Creative Commons BY 3.0"
              target="_blank"
            >CC 3.0 BY</a>
          </i18n>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<style scoped>
.swegram-title {
  margin: auto;
}

.swegram-title h1 {
  color: rgba(67, 77, 108);
  font-size: 3em;
  margin: auto;
  text-align: center;
}

h2 {
  color: #303133;
}

.icons-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.icons-container img {
  margin: 20px;
}

.link-container a {
  margin:20px;
}

.button-container {
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.button-container a {
  text-decoration: none;
}

.button-wrapper {
  margin: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 200px;
  height: 200px;
}

.button-wrapper span {
  margin-top: 20px;
  text-align: center;
}

.info-container {
  font-size: 75%;
  color: #606266;
}

.footer-container {
  font-size: 60%;
  text-align: right;
}
</style>
