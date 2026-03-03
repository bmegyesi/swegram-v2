<script setup>
import { ref, reactive, onMounted, getCurrentInstance } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { useI18n } from 'vue-i18n'
import { ElMessageBox, ElMessage } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue'
import UploadAnnotatedErrors from '@/components/errors/UploadAnnotatedErrors.vue';

const { t } = useI18n();
const props = defineProps({
  useFile: { type: Boolean, default: false },
  usePaste: { type: Boolean, default: false },
});
const emit = defineEmits(['uploaded']);

const router = useRouter();
const route = useRoute();
const { proxy } = getCurrentInstance();

const upload = ref(null);
const isUploading = ref(false);
const annotatedErrors = ref([]);
const pastedText = ref('');

const formData = reactive({
  annotated: false,
  checkTokenize: true,
  tokenizer: 'efselab',
  checkNormalization: false,
  spellchecker: 'histnorm',
  checkPOS: true,
  tagger: 'efselab',
  tagger_model: 'suc',
  parser: 'maltparser',
  parser_model: 'maltmodel_ud',
});

onMounted(() => {
  if (route.params.toolVersion === 'sv') {
    Object.assign(formData, {
      annotated: false,
      checkTokenize: true,
      tokenizer: 'efselab',
      checkNormalization: false,
      spellchecker: 'histnorm',
      checkPOS: true,
      tagger: 'efselab',
      tagger_model: 'suc',
      parser: 'maltparser',
      parser_model: 'maltmodel_ud',
    });
  } else if (route.params.toolVersion === 'en') {
    Object.assign(formData, {
      annotated: false,
      checkTokenize: true,
      tokenizer: 'udpipe',
      checkNormalization: false,
      spellchecker: 'histnorm_en',
      checkPOS: true,
      tagger: 'udpipe',
      tagger_model: 'ud',
      parser: 'udpipe',
      parser_model: 'ud',
    });
  }
});

function resetErrors() {
  annotatedErrors.value = [];
}

function updateTextList(textStatsList) {
  let textList = JSON.parse(localStorage.getItem('textList'));
  if (!textList) {
    textList = { en: [], sv: [] };
  }
  textStatsList.forEach((text) => {
    textList[text.fields.lang].push(text);
  });
  localStorage.setItem('textList', JSON.stringify(textList));
  updateMetadat(textStatsList);
}

function updateMetadat(texts) {
  let metadata = JSON.parse(localStorage.getItem('metadata'));
  if (!metadata) {
    metadata = { en: {}, sv: {} };
  }
  texts.forEach((text) => {
    const textMetadata = text.fields.labels;
    if (textMetadata) {
      const { lang } = text.fields;
      Object.keys(textMetadata).forEach((label) => {
        const value = textMetadata[label];
        if (Object.keys(metadata[lang]).includes(label)) {
          if (Object.keys(metadata[lang][label]).includes(value)) {
            metadata[lang][label][value].push([text.fields.text_id, text.fields.filename]);
          } else {
            metadata[lang][label][value] = [[text.fields.text_id, text.fields.filename]];
          }
        } else {
          metadata[lang][label] = {};
          metadata[lang][label][value] = [[text.fields.text_id, text.fields.filename]];
        }
      });
    }
  });
  localStorage.setItem('metadata', JSON.stringify(metadata));
}

function handleUploadSuccess(response) {
  isUploading.value = false;
  if (response.success === 0) {
    annotatedErrors.value = response.error_msg;
  } else {
    updateTextList(response.text_stats_list);
    ElMessage({
      message: t('uploadForm.uploadSuccessMsg'),
      type: 'success',
    });
    router.push(`/${route.params.toolVersion}/visualize`);
    emit('uploaded');
  }
}

function handleUploadFailure(error) {
  isUploading.value = false;
  ElMessage.error(
    proxy.$t('uploadForm.uploadFailedMsg', [error])
  )
}

function handleUploadOnProgress(event) {
  isUploading.value = event.percentage !== 100;
}

function beforeUploadCheck(file) {
  // eslint-disable-next-line no-console
  console.log('file type', file.type);
  const isTextFile = file.type === 'text/plain'
    || file.type === 'text/csv'
    || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    || file.type === 'application/msword'
    || file.type === 'application/vnd.oasis.opendocument.text'
    || file.type === 'application/rtf';
  const isFileTooBig = file.size / 1024 / 1024 > 100;
  if (!isTextFile) {
    ElMessage.error(
      proxy.$t('uploadForm.uploadErrNonText')
    )
  }
  if (isFileTooBig) {
    ElMessage.error(
      proxy.$t('uploadForm.uploadErrFileTooBig')
    )
  }

  return ElMessageBox.confirm(
    t('uploadForm.beforeUploadWarning'),
    '',
    { type: 'warning' }
  )
}

function uploadFile() {
  if (upload.value && upload.value.submit) {
    upload.value.submit();
  }
}

async function postPastedText() {
  const form = new FormData();
  Object.keys(formData).forEach((key) => {
    form.append(key, formData[key]);
  });
  form.append('use_paste', 'on');
  form.append('pasted_text', pastedText.value);

  isUploading.value = true;
  if (formData.annotated) {
    axios.put(uploadURL(), form).then((response) => {
      handleUploadSuccess(response.data);
    }).catch((err) => {
      handleUploadFailure(err);
    });
  } else {
    axios.post(uploadURL(), form).then((response) => {
      handleUploadSuccess(response.data);
    }).catch((err) => {
      handleUploadFailure(err);
    });
  }
}

function uploadURL() {
  return `/api/text/${route.params.toolVersion}`;
}
</script>

<template>
  <div v-loading="isUploading">
    <div style="text-align: center;">
      <div v-if="usePaste">
        <el-input
          v-model="pastedText"
          type="textarea"
          :autosize="{ minRows: 10, maxRows: 100 }"
          :placeholder="$t('uploadForm.pasteBoxPlaceholder')"
        />
        <el-button
          class="upload-btn"
          type="primary"
          @click="postPastedText()"
        >
          {{ $t('uploadForm.annotate') }}
        </el-button>
      </div>

      <div v-if="useFile">
        <div v-if="annotatedErrors.length !== 0">
          <upload-annotated-errors
            :errors="annotatedErrors"
            @clearErrors="resetErrors"
          />
        </div>
        <div v-else>
          <el-upload
            ref="upload"
            drag
            :auto-upload="false"
            :action="uploadURL()"
            :headers="{ 'X-CSRFToken': $cookies.get('csrftoken') }"
            :data="formData"
            :before-upload="beforeUploadCheck"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadFailure"
            :on-progress="handleUploadOnProgress"
            :name="formData.annotated ? 'file_to_analyze' : 'file_to_annotate'"
          >
            <el-icon>
              <UploadFilled />
            </el-icon>
            <div class="el-upload__text">
              {{ $t('uploadForm.uploadPrompt') }}
              <!-- Click or drag file to select file. Then press Upload -->
            </div>
          </el-upload>
          <el-button
            class="upload-btn"
            type="primary"
            @click="uploadFile"
          >
            {{ $t("uploadForm.upload") }}
          </el-button>
        </div>
      </div>
    </div>

    <h4>{{ $t('uploadForm.setting') }}</h4>
    <el-form
      :inline="true"
      :model="formData"
      label-positon="top"
    >
      <el-form-item :label="$t('uploadForm.tokenization')">
        <el-switch
          v-model="formData.checkTokenize"
          disabled
        />
      </el-form-item>

      <el-form-item :label="$t('uploadForm.normalization')">
        <el-switch v-model="formData.checkNormalization" />
      </el-form-item>

      <el-form-item :label="$t('uploadForm.posTaggingParsing')">
        <el-switch v-model="formData.checkPOS" />
      </el-form-item>
      <div v-if="useFile">
        <el-form-item>
          <el-checkbox
            v-model="formData.annotated"
            :label="$t('uploadForm.annotatedTextPrompt')"
            border
          />
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<style scoped>
.upload-btn {
  margin: 24px;
}
.el-upload-list {
  margin: 0 96px 0 96px;
}
</style>
