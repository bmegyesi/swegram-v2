<template>
  <el-container>
    <el-header><h2>{{ $t('uploadPage.annotateNewText') }}</h2></el-header>

    <el-main>
      <div
        v-show="!showTextForm"
        id="upload_annotate_main"
      >
        {{ $tc('uploadPage.uploadMessage1', 0) }}
        <div class="ui bulleted list">
          <div class="item">
            {{ $tc('uploadPage.uploadMessage1', 1) }}
          </div>
          <div class="item">
            {{ $tc('uploadPage.uploadMessage1', 2) }}
          </div>
        </div>
        {{ $tc('uploadPage.uploadMessage2', 0) }}
        <i>{{ $tc('uploadPage.uploadMessage2', 1) }}</i>
        {{ $tc('uploadPage.uploadMessage2', 2) }}
        <br><br><br>

        <center>
          <el-button @click="useFile = true">
            <i class="el-icon-upload" /> {{ $t('uploadPage.textUploadButton') }}
          </el-button>
          <el-button @click="usePaste = true">
            <i class="el-icon-document-copy" /> {{ $t('uploadPage.textPasteButton') }}
          </el-button>
        </center>
      </div>

      <div v-show="showTextForm">
        <el-page-header
          :content="$t('uploadForm.uploadTextFile')"
          :title="$t('uploadForm.back')"
          @back="showTextForm = false"
        />
        <upload-form
          :use-file="useFile"
          :use-paste="usePaste"
          style="margin-top: 20px"
          v-on="$listeners"
        />
      </div>
    </el-main>
  </el-container>
</template>

<script>
import UploadForm from './UploadForm.vue';

export default {
  components: {
    UploadForm,
  },
  data() {
    return {
      usePaste: false,
      useFile: false,
    };
  },
  computed: {
    showTextForm: {
      get() {
        return this.usePaste || this.useFile;
      },
      set(newValue) {
        if (newValue) {
          this.useFile = true;
          this.usePaste = false;
        } else {
          this.useFile = false;
          this.usePaste = false;
        }
      },
    },
  },
};
</script>
