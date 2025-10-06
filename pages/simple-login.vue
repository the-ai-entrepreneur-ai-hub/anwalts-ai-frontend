<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          ANWALTS.AI Login
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Test Login Page
        </p>
      </div>
      
      <div v-if="error" class="rounded-md bg-red-50 p-4">
        <div class="text-sm text-red-800">{{ error }}</div>
      </div>

      <div v-if="success" class="rounded-md bg-green-50 p-4">
        <div class="text-sm text-green-800">{{ success }}</div>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Email address"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>
        </div>

        <div class="text-sm text-gray-600">
          <p>Test credentials:</p>
          <p>Email: test@anwalts.ai</p>
          <p>Password: Test1234</p>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ loading ? 'Logging in...' : 'Sign in' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

const email = ref('test@anwalts.ai')
const password = ref('Test1234')
const loading = ref(false)
const error = ref('')
const success = ref('')
const config = useRuntimeConfig()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await $fetch<any>('/api/auth/login', {
      method: 'POST',
      body: {
        email: email.value,
        password: password.value
      }
    })

    if (response.success && response.token) {
      // Store auth data
      localStorage.setItem('auth_token', response.token)
      localStorage.setItem('user_id', response.user.id)
      localStorage.setItem('user_email', response.user.email)
      localStorage.setItem('user_name', response.user.name)
      localStorage.setItem('user_role', response.user.role)
      
      success.value = 'Login successful! Redirecting...'
      
      // Redirect to dashboard
      setTimeout(() => {
        navigateTo('/dashboard')
      }, 1000)
    } else {
      error.value = response.error || 'Login failed'
    }
  } catch (e: any) {
    console.error('Login error:', e)
    error.value = e.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
