<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
    dataList: { type: Array, default: () => [] },
    category: { type: String, default: '' },
    tagset: { type: String, default: '' },
})

const emit = defineEmits(['switchPos', 'changeShowType'])

const frequencyType = ref('showType')
const data = ref([])

watch(
    () => props.dataList,
    (newValue) => {
        const notDisplayAll = newValue.map((entry) => entry.model).includes(false)
        data.value = [{ pos: 'ALL', model: !notDisplayAll, frequency: null }, ...newValue]
    },
    { immediate: true }
)

function handlePoSSwitch(state, pos, f) {
    emit('switchPos', { state, pos, f })
}

function getTypePoS(value) {
    emit('changeShowType', value)
}
</script>

<template>
  <div class="frequency-container">
    <el-popover
      placement="right"
      width="150"
      trigger="click"
    >
      <el-table
        :data="data"
        height="300px"
      >
        <el-table-column
          width="80"
          prop="pos"
          :label="tagset.toUpperCase()"
        />

        <el-table-column
          label="Toggle"
          width="70"
        >
          <template #default="{ row }">
            <el-switch
              v-model="row.model"
              @change="handlePoSSwitch(row.model, row.pos, row.frequency)"
            />
          </template>
        </el-table-column>
      </el-table>

      <template #reference>
        <el-button>
          Select PoS
        </el-button>
      </template>
    </el-popover>

    <el-radio-group
      v-model="frequencyType"
      size="small"
      @change="getTypePoS"
    >
      <el-radio
        class="frequency-radio"
        value="showType"
        border
      >
        Show frequency statistics for type
      </el-radio>

      <el-radio
        class="frequency-radio"
        value="showPoS"
        border
      >
        Show frequency statistics for PoS
      </el-radio>
    </el-radio-group>
  </div>
</template>

<style scoped>
.frequency-container {
  display: flex;
}

.frequency-radio { 
  margin: 10px;
}

.el-button {
  margin: 0 10px 0 10px;
}

</style>
