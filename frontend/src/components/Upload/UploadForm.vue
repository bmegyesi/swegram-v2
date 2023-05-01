<template>
  <div v-loading="isUploading">
    <center>
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
            <i class="el-icon-upload" />
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
    </center>

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

<script>
import axios from 'axios';
import UploadAnnotatedErrors from './UploadAnnotatedErrors.vue';

export default {
  components: {
    UploadAnnotatedErrors,
  },
  props: ['useFile', 'usePaste'],
  data() {
    return {
      isUploading: false,
      annotatedErrors: [],
      formData: {
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
      },
      pastedText: '',
    };
  },
  mounted() {
    if (this.$route.params.toolVersion === 'sv') {
      this.formData = {
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
      };
    } else if (this.$route.params.toolVersion === 'en') {
      this.formData = {
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
      };
    }
  },
  methods: {
    resetErrors() {
      this.annotatedErrors = [];
    },
    updateTextList(textStatsList) {
      let textList = JSON.parse(localStorage.getItem('textList'));
      if (!(textList)) {
        textList = { en: [], sv: [] };
      }
      textStatsList.forEach((text) => {
        textList[text.fields.lang].push(text);
      });
      localStorage.setItem('textList', JSON.stringify(textList));
      this.updateMetadat(textStatsList);
    },
    updateMetadat(texts) {
      let metadata = JSON.parse(localStorage.getItem('metadata'));
      if (!(metadata)) {
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
    },
    handleUploadSuccess(response) {
      this.isUploading = false;
      if (response.success === 0) {
        this.annotatedErrors = response.error_msg;
      } else {
        this.updateTextList(response.text_stats_list);
        this.$message({
          message: this.$t('uploadForm.uploadSuccessMsg'),
          type: 'success',
        });
        this.$router.push(`/${this.$route.params.toolVersion}/visualize`);
        this.$emit('uploaded');
      }
    },
    handleUploadFailure(error) {
      this.isUploading = false;
      this.$message.error(this.$t('uploadForm.uploadFailedMsg', [error]));
    },
    handleUploadOnProgress(event) {
      this.isUploading = event.percentage !== 100;
    },
    beforeUploadCheck(file) {
      console.log('file type', file.type);
      const isTextFile = file.type === 'text/plain'
       || file.type === 'text/csv'
       || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
       || file.type === 'application/msword'
       || file.type === 'application/vnd.oasis.opendocument.text'
       || file.type === 'application/rtf';
      const isFileTooBig = file.size / 1024 / 1024 > 100;
      if (!isTextFile) {
        this.$message.error(this.$t('uploadForm.uploadErrNonText'));
      }
      if (isFileTooBig) {
        this.$message.error(this.$t('uploadForm.uploadErrFileTooBig'));
      }

      return new Promise((resolve, reject) => {
        if (isTextFile && !isFileTooBig) {
          this.$confirm(this.$t('uploadForm.beforeUploadWarning'), {
            type: 'warning',
          }).then(() => {
            resolve();
          }).catch(() => {
            reject();
          });
        } else {
          reject();
        }
      });
    },
    uploadFile() {
      this.$refs.upload.submit();
    },
    postPastedText() {
      const form = new FormData();
      Object.keys(this.formData).forEach((key) => {
        form.append(key, this.formData[key]);
      });
      form.append('use_paste', 'on');
      form.append('pasted_text', this.pastedText);

      this.isUploading = true;
      axios.post(this.uploadURL(), form).then((response) => {
        this.handleUploadSuccess(response.data);
      });
    },
    uploadURL() {
      // const tokenization = this.formData.checkTokenize ? 'tokenized' : 'untokenized';
      if (this.formData.annotated) {
        return `/upload/${this.$route.params.toolVersion}`; // This uploads annotated file, lang needed to be modified
      }
      return `/upload_annotate/${this.$route.params.toolVersion}`; // This actually means upload AND annotate
    //   return '/upload_annotate/'; // This actually means upload AND annotate
    },
  },
};
</script>

<style scoped>
.upload-btn {
  margin: 24px;
}
.el-upload-list {
  margin: 0 96px 0 96px;
}
</style>
