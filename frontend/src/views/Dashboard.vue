<script setup>
import axios from 'axios';
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { CircleCheck, Clock, DataAnalysis, Refresh, Warning } from '@element-plus/icons-vue';

import DefaultLayout from '@/layouts/DefaultLayout.vue';

const jobs = ref([]);
const tasks = ref([]);
const loading = ref(false);
const errorMessage = ref('');
const lastUpdated = ref(null);
let refreshTimer = null;

const stateMap = {
  0: { label: 'Created', type: 'info' },
  1: { label: 'Running', type: 'warning' },
  2: { label: 'Finished', type: 'success' }
};

const verdictMap = {
  0: { label: 'Passed', type: 'success' },
  1: { label: 'Failed', type: 'danger' },
  2: { label: 'Skipped', type: 'info' }
};

const orderedJobs = computed(() => {
  return [...jobs.value]
    .map((job) => ({
      ...job,
      tasks: job.tasks?.length ? job.tasks : tasks.value.filter((task) => task.job_id === job.id)
    }))
    .sort((a, b) => b.id - a.id);
});

const summary = computed(() => {
  const total = jobs.value.length;
  const running = jobs.value.filter((job) => job.state === 1).length;
  const failed = jobs.value.filter((job) => job.verdict === 1).length;
  const finished = jobs.value.filter((job) => job.state === 2).length;
  return { total, running, failed, finished };
});

async function fetchDashboard() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const [jobsResponse, tasksResponse] = await Promise.all([
      axios.get('/api/jobs/'),
      axios.get('/api/tasks/')
    ]);
    jobs.value = jobsResponse.data;
    tasks.value = tasksResponse.data;
    lastUpdated.value = new Date();
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || error.message || 'Unable to load dashboard data.';
  } finally {
    loading.value = false;
  }
}

function statusFor(value) {
  return stateMap[value] || { label: 'Unknown', type: 'info' };
}

function verdictFor(value) {
  if (value === null || value === undefined) {
    return { label: 'Pending', type: 'info' };
  }
  return verdictMap[value] || { label: 'Unknown', type: 'info' };
}

function progressFor(job) {
  const jobTasks = job.tasks || [];
  if (!jobTasks.length) {
    if (job.state === 2 && job.verdict === 0) {
      return 100;
    }
    return job.state === 1 ? 50 : 0;
  }
  const finished = jobTasks.filter((task) => task.state === 2).length;
  return Math.round((finished / jobTasks.length) * 100);
}

function progressStatus(job) {
  if (job.verdict === 1) {
    return 'exception';
  }
  if (job.state === 2 && job.verdict === 0) {
    return 'success';
  }
  return undefined;
}

function formatDate(value) {
  if (!value) {
    return '-';
  }
  return value;
}

function formatUpdatedAt() {
  if (!lastUpdated.value) {
    return '-';
  }
  return lastUpdated.value.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

onMounted(() => {
  fetchDashboard();
  refreshTimer = window.setInterval(fetchDashboard, 5000);
});

onUnmounted(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
  }
});
</script>

<template>
  <default-layout>
    <section class="dashboard-page">
      <div class="dashboard-header">
        <div>
          <h2>Annotation dashboard</h2>
          <p>Track annotation jobs and the tasks that make up each processing run.</p>
        </div>
        <div class="dashboard-actions">
          <span class="last-updated">Updated {{ formatUpdatedAt() }}</span>
          <el-button :loading="loading" :icon="Refresh" @click="fetchDashboard">
            Refresh
          </el-button>
        </div>
      </div>

      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        class="dashboard-alert"
      />

      <div class="summary-grid">
        <div class="summary-tile">
          <el-icon><DataAnalysis /></el-icon>
          <span>Total jobs</span>
          <strong>{{ summary.total }}</strong>
        </div>
        <div class="summary-tile">
          <el-icon><Clock /></el-icon>
          <span>Running</span>
          <strong>{{ summary.running }}</strong>
        </div>
        <div class="summary-tile">
          <el-icon><CircleCheck /></el-icon>
          <span>Finished</span>
          <strong>{{ summary.finished }}</strong>
        </div>
        <div class="summary-tile">
          <el-icon><Warning /></el-icon>
          <span>Failed</span>
          <strong>{{ summary.failed }}</strong>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="orderedJobs"
        class="jobs-table"
        row-key="id"
        empty-text="No annotation jobs yet"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="task-panel">
              <el-table
                :data="row.tasks || []"
                size="small"
                row-key="id"
                empty-text="No tasks recorded for this job"
              >
                <el-table-column prop="id" label="Task ID" width="90" />
                <el-table-column prop="name" label="Task" min-width="190" />
                <el-table-column label="State" width="120">
                  <template #default="{ row: task }">
                    <el-tag :type="statusFor(task.state).type" effect="plain">
                      {{ statusFor(task.state).label }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Verdict" width="120">
                  <template #default="{ row: task }">
                    <el-tag :type="verdictFor(task.verdict).type" effect="plain">
                      {{ verdictFor(task.verdict).label }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="Created" min-width="170" />
                <el-table-column prop="updated_at" label="Updated" min-width="170" />
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="id" label="Job ID" width="80" />
        <el-table-column prop="job_name" label="Job Name" width="120" />
        <el-table-column prop="filename" label="Text" min-width="220" />
        <el-table-column prop="language" label="Language" width="100" />
        <el-table-column label="Progress" min-width="180">
          <template #default="{ row }">
            <el-progress
              :percentage="progressFor(row)"
              :status="progressStatus(row)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        <el-table-column label="State" width="120">
          <template #default="{ row }">
            <el-tag :type="statusFor(row.state).type" effect="dark">
              {{ statusFor(row.state).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Verdict" width="120">
          <template #default="{ row }">
            <el-tag :type="verdictFor(row.verdict).type" effect="plain">
              {{ verdictFor(row.verdict).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Tasks" width="90">
          <template #default="{ row }">
            {{ row.tasks?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="Created" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </section>
  </default-layout>
</template>

<style scoped>
.dashboard-page {
  box-sizing: border-box;
  max-width: 1180px;
  margin: 0 auto;
  padding: 18px 12px 36px;
  background: var(--el-bg-color);
  color: var(--el-text-color-primary);
  min-height: calc(100vh - 150px);
}

.dashboard-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 18px;
}

.dashboard-header h2 {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 650;
  color: var(--el-text-color-primary);
}

.dashboard-header p {
  margin: 0;
  color: var(--el-text-color-regular);
}

.dashboard-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.last-updated {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.dashboard-alert {
  margin-bottom: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.summary-tile {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 4px 10px;
  align-items: center;
  padding: 14px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  background: var(--el-fill-color-extra-light);
}

.summary-tile .el-icon {
  grid-row: span 2;
  font-size: 22px;
  color: var(--el-color-primary);
}

.summary-tile span {
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.summary-tile strong {
  font-size: 24px;
  line-height: 1;
}

.jobs-table {
  width: 100%;
}

.task-panel {
  padding: 8px 24px 18px 48px;
  background: var(--el-fill-color-lighter);
}

@media (max-width: 900px) {
  .dashboard-header {
    flex-direction: column;
  }

  .dashboard-actions {
    justify-content: flex-start;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
