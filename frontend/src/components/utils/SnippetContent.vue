<script setup>
import { ref, watch, onMounted, toRef } from 'vue'

const props = defineProps({
  content: { type: String, default: '', required: false },
  level: { type: String, default: '', required: false },
})

const content = toRef(props, 'content')
const length = ref(content.value ? content.value.length : 0)
const end = ref(0)
const step = ref(0)

watch(content, (newVal) => {
  length.value = newVal ? newVal.length : 0
})

const setLimits = (level) => {
  if (level === 'sent') {
    end.value = 200
    step.value = 200
  } else if (level === 'para') {
    end.value = 500
    step.value = 500
  } else if (level === 'text') {
    end.value = 2000
    step.value = 2000
  } else {
    end.value = 0
    step.value = 0
  }
}

onMounted(() => setLimits(props.level))
watch(() => props.level, (l) => setLimits(l))

function showmore() {
  end.value += step.value
}
</script>

<template>
  <div>
    {{ content.slice(0, end).split(' ').slice(0,).join(' ') }}
    <el-button
      v-if="end < content.length - 1"
      link
      @click="showmore()"
    >
      ...
    </el-button>
  </div>
</template>
