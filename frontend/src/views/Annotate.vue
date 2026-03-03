<script setup>
import { ref, computed } from 'vue';
import Form from '@/components/upload/Form.vue';
import { DocumentCopy, UploadFilled } from '@element-plus/icons-vue'

import DefaultLayout from '@/layouts/DefaultLayout.vue';

const usePaste = ref(false);
const useFile = ref(false);

const showTextForm = () => usePaste.value || useFile.value

function openFileUpload() {
  useFile.value = true
  usePaste.value = false
}

function openPasteUpload() {
  usePaste.value = true
  useFile.value = false
}

function closeForm() {
  useFile.value = false
  usePaste.value = false
}

</script>

<template>
  <default-layout>
    <el-container>
      <el-header>
        <h2>{{ $t('uploadPage.annotateNewText') }}</h2>
      </el-header>
      <el-main>
        <div
          v-show="!showTextForm()"
          id="upload_annotate_main"
        >
          {{ $t('uploadPage.uploadMessage1') }}
          <br>
          {{ $t('uploadPage.uploadMessage2') }}
          <br><br><br>

          <div style="text-align: center;">
            <el-button link class="link-bordered" @click="openFileUpload">
              <el-icon size="22">
                <UploadFilled />
              </el-icon>
              <span>{{ $t('uploadPage.textUploadButton') }}</span>
            </el-button>
            <el-button link @click="openPasteUpload" class="link-bordered">
              <el-icon size="22">
                <DocumentCopy />
              </el-icon>
              <span>{{ $t('uploadPage.textPasteButton') }}</span>
            </el-button>
          </div>
        </div>

        <div v-show="showTextForm()">
          <el-page-header
            :content="$t('uploadForm.uploadTextFile')"
            :title="$t('uploadForm.back')"
            @back="closeForm"
          />
          <Form
            :use-file="useFile"
            :use-paste="usePaste"
            style="margin-top: 20px"
            v-bind="$attrs"
          />
        </div>
      </el-main>
    </el-container>
  </default-layout>
</template>

<style scoped>
:deep(.el-button.link-bordered) {
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 6px 12px;
}

:deep(.el-button.link-bordered:hover) {
  background-color: var(--el-fill-color-light);
}
</style>
