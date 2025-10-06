<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
    <div class="max-w-md w-full p-8">
      <h1 class="text-3xl font-bold text-white text-center mb-8">AUTH TEST PAGE</h1>
      
      <!-- Simple test buttons -->
      <div class="space-y-4">
        <button 
          @click="testModalOpen"
          class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-all"
        >
          TEST: Open Modal
        </button>
        
        <button 
          @click="testDirectAuth"
          class="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-all"
        >
          TEST: Direct Auth
        </button>
        
        <a 
          href="/api/auth/test"
          class="block w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-purple-700 transition-all text-center"
        >
          TEST: Server Auth
        </a>
        
        <NuxtLink 
          to="/dashboard?auth=test&demo=true"
          class="block w-full bg-orange-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-orange-700 transition-all text-center"
        >
          TEST: Direct Dashboard
        </NuxtLink>
      </div>
      
      <div class="mt-8 text-white text-center">
        <p>Modal State: {{ showModal ? 'OPEN' : 'CLOSED' }}</p>
        <p>Click Count: {{ clickCount }}</p>
      </div>
    </div>
    
    <!-- Test Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-8 rounded-lg max-w-sm w-full mx-4">
        <h2 class="text-xl font-bold mb-4">AUTH MODAL WORKS!</h2>
        <p class="mb-4">This proves the modal system is working correctly.</p>
        <button 
          @click="testGoogleAuth"
          class="w-full bg-blue-500 text-white py-2 px-4 rounded mb-2"
        >
          Google Auth
        </button>
        <button 
          @click="testEmailAuth"
          class="w-full bg-gray-500 text-white py-2 px-4 rounded mb-2"
        >
          Email Auth
        </button>
        <button 
          @click="closeModal"
          class="w-full bg-red-500 text-white py-2 px-4 rounded"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

definePageMeta({
  layout: false
})

const showModal = ref(false)
const clickCount = ref(0)

const testModalOpen = () => {
  clickCount.value++
  console.log('🎯 TEST BUTTON CLICKED!', clickCount.value)
  showModal.value = true
}

const testDirectAuth = () => {
  clickCount.value++
  console.log('🎯 DIRECT AUTH CLICKED!', clickCount.value)
  navigateTo('/dashboard?auth=direct&demo=true')
}

const testGoogleAuth = () => {
  console.log('🎯 GOOGLE AUTH TEST')
  navigateTo('/auth/google')
}

const testEmailAuth = () => {
  console.log('🎯 EMAIL AUTH TEST')
  navigateTo('/dashboard?auth=email&demo=true')
}

const closeModal = () => {
  showModal.value = false
}

onMounted(() => {
  console.log('✅ TEST PAGE MOUNTED - All buttons should work!')
})
</script>
