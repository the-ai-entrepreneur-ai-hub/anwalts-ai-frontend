import os

# Template content
content = '''<template>
  <div class="min-h-screen p-6 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold text-white mb-2 flex items-center">
        <i data-lucide="layout-template" class="mr-3 text-purple-400"></i>
        Templates Dashboard
      </h1>
      <p class="text-slate-300">Manage and analyze your legal document templates</p>
    </div>

    <!-- Template Performance Dashboard -->
    <div class="template-usage-analytics mb-8">
      <h2 class="text-2xl font-semibold text-white mb-6 flex items-center">
        <i data-lucide="trending-up" class="mr-2 text-green-400"></i>
        Template Performance Dashboard
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Success Rate Card -->
        <div class="analytics-card backdrop-blur-lg bg-white/10 rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <div class="p-3 bg-green-500/20 rounded-full">
              <i data-lucide="check-circle" class="text-green-400 w-6 h-6"></i>
            </div>
            <span class="text-green-400 text-sm font-medium">+12%</span>
          </div>
          <h3 class="text-white text-lg font-semibold mb-1">Success Rate</h3>
          <p class="text-3xl font-bold text-green-400 mb-2">94.2%</p>
          <p class="text-slate-400 text-sm">Last 30 days</p>
        </div>

        <!-- Total Templates Card -->
        <div class="analytics-card backdrop-blur-lg bg-white/10 rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <div class="p-3 bg-blue-500/20 rounded-full">
              <i data-lucide="file-text" class="text-blue-400 w-6 h-6"></i>
            </div>
            <span class="text-blue-400 text-sm font-medium">+5</span>
          </div>
          <h3 class="text-white text-lg font-semibold mb-1">Total Templates</h3>
          <p class="text-3xl font-bold text-blue-400 mb-2">247</p>
          <p class="text-slate-400 text-sm">Active templates</p>
        </div>

        <!-- Usage This Month Card -->
        <div class="analytics-card backdrop-blur-lg bg-white/10 rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <div class="p-3 bg-purple-500/20 rounded-full">
              <i data-lucide="activity" class="text-purple-400 w-6 h-6"></i>
            </div>
            <span class="text-purple-400 text-sm font-medium">+23%</span>
          </div>
          <h3 class="text-white text-lg font-semibold mb-1">Usage This Month</h3>
          <p class="text-3xl font-bold text-purple-400 mb-2">1,847</p>
          <p class="text-slate-400 text-sm">Documents generated</p>
        </div>

        <!-- Average Processing Time Card -->
        <div class="analytics-card backdrop-blur-lg bg-white/10 rounded-2xl p-6 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <div class="p-3 bg-orange-500/20 rounded-full">
              <i data-lucide="clock" class="text-orange-400 w-6 h-6"></i>
            </div>
            <span class="text-green-400 text-sm font-medium">-8%</span>
          </div>
          <h3 class="text-white text-lg font-semibold mb-1">Avg Processing</h3>
          <p class="text-3xl font-bold text-orange-400 mb-2">2.3s</p>
          <p class="text-slate-400 text-sm">Response time</p>
        </div>
      </div>
    </div>
</template>

<script setup>
const showClauseModal = ref(false)
const modalTitle = ref('')
const modalClauses = ref([])

// Initialize Lucide icons
onMounted(() => {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons()
  }
})
</script>

<style scoped>
.progress-bar {
  transition: width 0.8s ease-in-out;
}

.analytics-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analytics-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.template-usage-analytics .progress-bar {
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  animation: progressLoad 1.2s ease-in-out;
}

@keyframes progressLoad {
  from {
    width: 0%;
  }
}
</style>'''

# Write to file
with open('pages/templates.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Template file created successfully!')
