<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const visible = ref(false)
const title = ref("")
const line1 = ref("")
const line2 = ref("")
const titlestyle = ref([])
const ok = ref("")
const cancel = ref("")

let translated
let cbconfirm = null

function showConfirm(callback, options) {
  visible.value = true
  translated = !!options.translated
  line1.value = translated ? t(options.line1) : options.line1
  line2.value = translated ? t(options.line2) : options.line2
  title.value = translated ? t(options.title) : options.title
  ok.value = translated ? t("OK") : "OK"
  cancel.value = translated ? t("Cancel") : "Cancel"
  cbconfirm = callback
  let styles = ["borderline"]
  if (options.bgcolor) {
    styles.push("bg-" + options.bgcolor)
  }
  if (options.fgcolor) {
    styles.push("text-" + options.fgcolor)
  }
  titlestyle.value = styles.join(" ")
}

function confirm() {
  visible.value = false
  if (cbconfirm) cbconfirm()
}

defineExpose({ showConfirm })
</script>
<template>
  <VDialog v-model="visible" width="20em">
    <VCard>
      <VCardTitle :class="titlestyle">
        {{ title }}
      </VCardTitle>
      <VCardText class="borderline">
        <div>{{ line1 }}</div>
        <div v-if="line2" class="my-2">{{ translated ? t(line2) : line2 }}</div>
      </VCardText>
      <VCardActions>
        <VSpacer />
        <v-btn @click="confirm">{{ ok }}</v-btn>
        <v-btn @click="visible = false">{{ cancel }}</v-btn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.borderline {
  border-bottom: 1px solid #ddd;
}
</style>