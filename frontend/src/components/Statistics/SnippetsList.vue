<script setup>
import axios from 'axios';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import SnippetStatisticsTable from '@/components/statistics/SnippetStatisticsTable.vue';
import SnippetContent from '@/components/utils/SnippetContent.vue';

const props = defineProps({
  snippets: { type: Array, default: () => [] },
  dataSnippets: { type: Array, default: () => [] },
  level: { type: String, default: 'text' },
  total: { type: Number, default: 0 },
  contentLoading: { type: Boolean, default: false },
});

const emit = defineEmits(['currentPage']);
const route = useRoute();

const showOverviewOrDetail = ref('content');
const overviewData = ref({});
const currentPage = ref(1);
const loadingOverviewData = ref(false);
const showContent = ref(true);
const showOverview = ref(false);
const initializedOverview = ref(false);

watch(showOverview, (newValue) => {
  if (newValue && !initializedOverview.value) {
    loadingOverviewData.value = true;
    fetchOverviewData();
  }
});

function handleCurrentChange(val) {
  emit('currentPage', { page: val });
}

function handleShowContentOrOverview(obj) {
  if (obj.props.name === 'content') {
    showContent.value = true;
    showOverview.value = false;
  } else if (obj.props.name === 'overview') {
    showContent.value = false;
    showOverview.value = true;
  }
}

async function fetchOverviewData() {
  if (!localStorage.textList) {
    localStorage.setItem('textList', JSON.stringify({}));
  }
  const lang = route.params.toolVersion;
  const overviewURL = `/api/features/${props.level}s`;
  try {
    const response = await axios.post(overviewURL, {
      texts: JSON.parse(localStorage.textList),
      lang,
    });
    overviewData.value = { data: response.data.data };
    initializedOverview.value = true;
  } finally {
    loadingOverviewData.value = false;
  }
}
</script>

<template>
  <el-container>
    <el-tabs
      v-model="showOverviewOrDetail"
      type="card"
      @tab-click="handleShowContentOrOverview"
    >
      <el-tab-pane
        label="Overview"
        name="overview"
      >
        <el-card shadow="hover">
          <div
            slot="header"
            class="clearfix"
          >
            <span>Statistics</span>
          </div>
          <snippet-statistics-table
            :statistics-table-data="overviewData"
            :loading-overview="loadingOverviewData"
          />
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="Content" name="content">
        <div v-loading="contentLoading">
          <el-card
            v-for="(snippet, i) in snippets"
            :key="i"
            shadow="hover"
          >
            <template #header>
              <div class="clearfix">
                <span>{{ (currentPage - 1) * 10 + 1 + i }}</span>

                <el-popover
                  placement="left"
                  title="Statistics"
                  width="800"
                  trigger="click"
                >
                  <template v-if="dataSnippets[i]">
                    <snippet-statistics-table
                      :statistics-table-data="dataSnippets[i]"
                      :level="level"
                    />
                  </template>

                  <template #reference>
                    <el-button link style="float: right; padding: 3px 0">
                      Detail
                    </el-button>
                  </template>
                </el-popover>
              </div>
            </template>

            <snippet-content
              :content="snippet"
              :level="level"
            />
          </el-card>

          <el-pagination
            :hide-on-single-page="true"
            v-model:current-page="currentPage"
            :page-size="10"
            layout="prev, pager, next, jumper"
            :total="total"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-container>
</template>

<style scoped>
.el-card {
  margin: 4px;
}

.el-container {
  display: block;
}
</style>
