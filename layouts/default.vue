<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <NuxtLink to="/" class="flex-shrink-0 flex items-center">
              <h1 class="text-xl font-bold text-blue-600">Anwalts AI</h1>
            </NuxtLink>
          </div>
          <div class="flex items-center space-x-4">
            <NuxtLink to="/login" class="text-gray-700 hover:text-blue-600">Login</NuxtLink>
            <NuxtLink to="/register" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              Register
            </NuxtLink>
          </div>
        </div>
      </nav>
    </header>
    
    <main>
      <slot />
    </main>
    
    <footer class="bg-gray-800 text-white mt-auto">
      <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <p class="text-center text-gray-300">&copy; 2024 Anwalts AI. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>