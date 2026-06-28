<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";

// communication
const { $backend } = useNuxtApp()
// data fetching

async function getExcel() {
  let response
  try {
    response = await $backend("test", "excel")
    console.log("reponse on generate", response)
  }
  catch (error) {
    console.error("Error downloading the Excel file:", error);
    return    
  }
  const blob = response.data;
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = "test.xlsx";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);  
}

definePageMeta({
  layout: "nomenu",
});
</script>

<template>
<div>
<h1>Test Excel file</h1>
<button v-on:click="getExcel">Load Excel</button>
</div>
</template>

