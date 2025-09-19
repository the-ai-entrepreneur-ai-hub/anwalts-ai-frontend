<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-4xl font-bold text-white mb-8 text-center">🔐 AUTH TESTING PAGE</h1>
      
      <!-- Test Credentials -->
      <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl mb-8">
        <h2 class="text-2xl font-bold text-white mb-4">📋 Available Test Credentials</h2>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="bg-green-500/20 p-4 rounded-lg">
            <h3 class="text-lg font-semibold text-white">Admin User</h3>
            <p class="text-green-200">Email: <code>admin@anwalts.ai</code></p>
            <p class="text-green-200">Password: <code>admin123</code></p>
            <p class="text-sm text-green-300">Role: Administrator</p>
          </div>
          
          <div class="bg-blue-500/20 p-4 rounded-lg">
            <h3 class="text-lg font-semibold text-white">Demo User</h3>
            <p class="text-blue-200">Email: <code>demo@anwalts.ai</code></p>
            <p class="text-blue-200">Password: <code>demo123</code></p>
            <p class="text-sm text-blue-300">Role: Demo</p>
          </div>
          
          <div class="bg-purple-500/20 p-4 rounded-lg">
            <h3 class="text-lg font-semibold text-white">Regular User</h3>
            <p class="text-purple-200">Email: <code>user@anwalts.ai</code></p>
            <p class="text-purple-200">Password: <code>user123</code></p>
            <p class="text-sm text-purple-300">Role: User</p>
          </div>
          
          <div class="bg-orange-500/20 p-4 rounded-lg">
            <h3 class="text-lg font-semibold text-white">Test User</h3>
            <p class="text-orange-200">Email: <code>test@example.com</code></p>
            <p class="text-orange-200">Password: <code>test123</code></p>
            <p class="text-sm text-orange-300">Role: User</p>
          </div>
        </div>
      </div>
      
      <!-- Login Form -->
      <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl mb-8">
        <h2 class="text-2xl font-bold text-white mb-4">🔑 Test Login Form</h2>
        <form @submit.prevent="testLogin" class="space-y-4">
          <div>
            <label class="block text-white mb-2">Email:</label>
            <input 
              v-model="loginForm.email" 
              type="email" 
              class="w-full p-3 rounded-lg bg-white/20 text-white placeholder-white/60"
              placeholder="Enter email (try admin@anwalts.ai)"
            >
          </div>
          <div>
            <label class="block text-white mb-2">Password:</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              class="w-full p-3 rounded-lg bg-white/20 text-white placeholder-white/60"
              placeholder="Enter password (try admin123)"
            >
          </div>
          <button 
            type="submit" 
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {{ loading ? 'Testing...' : 'Test Login' }}
          </button>
        </form>
        
        <div v-if="result" class="mt-4 p-4 rounded-lg" :class="result.success ? 'bg-green-500/20' : 'bg-red-500/20'">
          <pre class="text-white text-sm">{{ JSON.stringify(result, null, 2) }}</pre>
        </div>
      </div>
      
      <!-- Quick Test Buttons -->
      <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl mb-8">
        <h2 class="text-2xl font-bold text-white mb-4">⚡ Quick Tests</h2>
        <div class="grid md:grid-cols-4 gap-4">
          <button @click="quickLogin('admin@anwalts.ai', 'admin123')" class="bg-green-600 text-white py-3 rounded-lg hover:bg-green-700">
            Test Admin
          </button>
          <button @click="quickLogin('demo@anwalts.ai', 'demo123')" class="bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700">
            Test Demo
          </button>
          <button @click="quickLogin('user@anwalts.ai', 'user123')" class="bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700">
            Test User
          </button>
          <button @click="quickLogin('wrong@email.com', 'wrong')" class="bg-red-600 text-white py-3 rounded-lg hover:bg-red-700">
            Test Wrong
          </button>
        </div>
      </div>
      
      <!-- Navigation -->
      <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
        <h2 class="text-2xl font-bold text-white mb-4">🧭 Navigation</h2>
        <div class="flex gap-4">
          <NuxtLink to="/" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            ← Back to Landing
          </NuxtLink>
          <NuxtLink to="/dashboard" class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">
            Dashboard →
          </NuxtLink>
          <NuxtLink to="/test-auth" class="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700">
            Button Tests
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

definePageMeta({
  layout: false
})

const loading = ref(false)
const result = ref(null)

const loginForm = reactive({
  email: '',
  password: ''
})

const testLogin = async () => {
  loading.value = true
  result.value = null
  
  try {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: {
        email: loginForm.email,
        password: loginForm.password
      }
    })

    result.value = response

    if (response?.success && response?.user) {
      localStorage.setItem('auth_user', JSON.stringify(response.user))
      localStorage.setItem('auth_success', 'true')
      setTimeout(() => {
        navigateTo('/dashboard')
      }, 1200)
    }
  } catch (error) {
    result.value = {
      success: false,
      message: '❌ Login error',
      error: error?.statusMessage || error?.message || 'Unknown error'
    }
  } finally {
    loading.value = false
  }
}

const quickLogin = (email, password) => {
  loginForm.email = email
  loginForm.password = password
  testLogin()
}

onMounted(() => {
  console.log('🧪 LOGIN TEST PAGE LOADED')
  console.log('📋 Available credentials:')
  console.log('Admin: admin@anwalts.ai / admin123')
  console.log('Demo: demo@anwalts.ai / demo123') 
  console.log('User: user@anwalts.ai / user123')
  console.log('Test: test@example.com / test123')
})
</script>