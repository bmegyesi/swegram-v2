<script setup>
import { computed, toRefs } from 'vue';
import DisplacyImage from '@/components/visualize/DisplacyImage.vue';

const props = defineProps({
    snippets: { type: Array, default: () => [] },
    metaData: { type: Array, default: () => [] },
    textName: { type: String, default: null },
    pageSize: { type: Number, default: null },
    pageIndex: { type: Number, default: null },
    parsed: { type: Boolean, default: false },
});

const { snippets, metaData, textName, pageSize, pageIndex, parsed } = toRefs(props);
const showMetadata = computed(() => props.metaData.length > 0);

</script>

<template>
  <div>
    <el-row>
      <div class="section-name">
        <h3>{{ props.textName.split('.').slice(0, props.textName.split('.').length-1).join('.') }}</h3>
      </div>
    </el-row>
    <!-- <el-row
      v-show="showMetadata"
    >
      <div class="section-metadata">
        <h5>Metadata:</h5>
        <span>
          <el-tag
            v-for="(label, i) in metaData"
            :key="i"
            type="info"
          >
            {{ label[0] }} : {{ label[1] }}
          </el-tag>
        </span>
      </div>
    </el-row> -->
    <el-row class="section-body">
      <el-collapse>
        <el-collapse-item
          v-for="(snippet, i) in props.snippets"
          :key="i"
        >
          <template #title>
            <div class="snippet-title">
              <span>{{ snippet.tokens[0].text_id }}&nbsp;</span>
              <span
                v-for="(t, j) in snippet.tokens"
                :key="j"
                :class="t.highlight"
              >{{ t.form }}&nbsp;</span>
            </div>
          </template>
          <div
            class="snippet-sentence-tags"
          >
            <el-popover
              v-for="(token, k) in snippet.tokens"
              :key="k"
              :width="400"
              placement="top"
              trigger="click"
            >
              <h4>{{ $t('visualize.markedToken') }}</h4>
              {{ $t('visualize.form') }}: <span>{{ token.form }}</span><br>
              {{ $t('visualize.norm') }}: <span>{{ token.norm }}</span><br>
              {{ $t('visualize.lemma') }}: <span>{{ token.lemma }}</span><br>
              {{ $t('visualize.upos') }}: <span>{{ token.upos }}</span><br>
              {{ $t('visualize.xpos') }}: <span>{{ token.xpos }}</span><br>
              {{ $t('visualize.feats') }}: <span>{{ token.feats }}</span><br>
              {{ $t('visualize.ufeats') }}: <span>{{ token.ufeats }}</span><br>
              {{ $t('visualize.head') }}: <span>{{ token.head }}</span><br>
              {{ $t('visualize.deprel') }}: <span>{{ token.deprel }}</span><br>
              {{ $t('visualize.deps') }}: <span>{{ token.deps }}</span><br>
              {{ $t('visualize.misc') }}: <span>{{ token.misc }}</span><br>
              {{ $t('visualize.dependencyLength') }}: <span>{{ token.dep_length }}</span><br>
              {{ $t('visualize.stig') }}: <span>{{ token.path }}</span><br>
              <template #reference>
                <el-tag>
                  {{ token.form }}
                  <el-popover
                    v-if="token.compound_originals"
                    placement="top"
                    trigger="click"
                  >
                    <h4>{{ $t('visualize.markedToken') }}</h4>
                    {{ $t('visualize.form') }}: <span>{{ token.form }}</span><br>
                    {{ $t('visualize.norm') }}: <span>{{ token.norm }}</span><br>
                    {{ $t('visualize.lemma') }}: <span>{{ token.lemma }}</span><br>
                    {{ $t('visualize.upos') }}: <span>{{ token.upos }}</span><br>
                    {{ $t('visualize.xpos') }}: <span>{{ token.xpos }}</span><br>
                    {{ $t('visualize.feats') }}: <span>{{ token.feats }}</span><br>
                    {{ $t('visualize.ufeats') }}: <span>{{ token.ufeats }}</span><br>
                    {{ $t('visualize.head') }}: <span>{{ token.head }}</span><br>
                    {{ $t('visualize.deprel') }}: <span>{{ token.deprel }}</span><br>
                    {{ $t('visualize.deps') }}: <span>{{ token.deps }}</span><br>
                    {{ $t('visualize.misc') }}: <span>{{ token.misc }}</span><br>
                    {{ $t('visualize.dependencyLength') }}: <span>{{ token.dep_length }}</span><br>
                    {{ $t('visualize.stig') }}: <span>{{ token.path }}</span><br>
                    <template #reference><b>{{ token.norm }}</b></template>
                  </el-popover>
                </el-tag>
              </template>
            </el-popover>
          </div>
          <div
            v-if="parsed"
            class="snippet-data-container"
          >
            <displacy-image
              class="displacy-container"
              :sentence="snippet"
            />
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-row>
  </div>
</template>

<style scoped>

.highlight {
  color: red;
  font-weight: bold;
}

.section-name {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.section-name h3 {
  margin-right: 10px;
}

.section-name {
  flex-flow: wrap;
}

.section-body {
  margin: 0 0 0 30px;
}

.snippet-title {
  height: 48px;
  width: 100%;
  overflow: hidden;
}

.snippet-data-container {
  display: flex;
  margin: 4px;
  justify-content: center;
}

.displacy-container {
  width: 80%;
  max-height: 400px;
}

.el-tag {
  margin: 4px;
}

</style>
