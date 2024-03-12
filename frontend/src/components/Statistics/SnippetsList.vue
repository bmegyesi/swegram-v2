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
      <el-tab-pane
        v-loading="contentLoading"
        label="Content"
        name="content"
      >
        <el-card
          v-for="(snippet, i) in snippets"
          :key="i"
          shadow="hover"
        >
          <div
            slot="header"
            class="clearfix"
          >
            <span>{{ (currentPage-1)*10 + 1 + i }}</span>
            <el-popover
              placement="left"
              title="Statistics"
              width="800"
              trigger="click"
            >
              <snippet-statistics-table
                :statistics-table-data="dataSnippets[i]"
                :level="level"
              />
              <el-button
                slot="reference"
                style="float: right; padding: 3px 0"
                type="text"
              >
                Detail
              </el-button>
            </el-popover>
          </div>
          <div>
            <snippet-content
              :content="snippet"
              :level="level"
            />
          </div>
        </el-card>
        <el-pagination
          :hide-on-single-page="true"
          :current-page.sync="currentPage"
          :page-size="10"
          layout="prev, pager, next, jumper"
          :total="total"
          @current-change="handleCurrentChange"
        />
      </el-tab-pane>
    </el-tabs>
  </el-container>
</template>

<script>
import axios from 'axios';
import SnippetStatisticsTable from './SnippetStatisticsTable.vue';
import SnippetContent from '../Common/SnippetContent.vue';

export default {
  components: {
    SnippetStatisticsTable,
    SnippetContent,
  },
  props: {
    snippets: {
      type: Array,
      default: () => [],
      required: false,
    },
    dataSnippets: {
      type: Array,
      default: () => [],
      required: false,
    },
    level: {
      type: String,
      default: null,
      required: false,
    },
    total: {
      type: Number,
      default: 0,
      required: false,
    },
    contentLoading: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      showOverviewOrDetail: '',
      overviewData: {},
      currentPage: 1,
      loadingOverviewData: false,
      showContent: true,
      showOverview: false,
      initializedOverview: false,
    };
  },
  watch: {
    showOverview(newValue) {
      if (newValue && !this.initializedOverview) {
        this.loadingOverviewData = true;
        this.fetchOverviewData();
      }
    },
  },
  methods: {
    handleCurrentChange(val) {
      this.$emit('currentPage', { page: val });
    },
    handleShowContentOrOverview(obj) {
      if (obj.name === 'content') {
        this.showContent = true;
        this.showOverview = false;
      } if (obj.name === 'overview') {
        this.showContent = false;
        this.showOverview = true;
      }
    },
    fetchOverviewData() {
      if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
      }
      const lang = this.$route.params.toolVersion;
      const overviewURL = `/api/features/${this.$props.level}s`;
      axios
        .post(overviewURL, {
          texts: JSON.parse(localStorage.textList),
          lang,
        })
        .then((response) => {
          this.overviewData = { data: response.data.data };
        })
        .then(() => {
          this.loadingOverviewData = false;
        });
    },
  },
};
</script>

<style scoped>
.el-card {
  margin: 4px;
}

.el-container {
  display: block;
}
</style>
