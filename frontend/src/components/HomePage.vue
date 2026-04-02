<template>
  <div class="container">
    <nav class="nav-bar">
      <router-link :to="{ name: 'home' }">Home</router-link>
      <router-link :to="{ name: 'todo-list' }">All Todos</router-link>
      <router-link :to="{ name: 'create-todo' }">Create Todo</router-link>
      <router-link v-if="isAuthenticated" :to="{ name: 'calendar' }">Calendar</router-link>
      <router-link v-if="!isAuthenticated" :to="{ name: 'login' }">Login</router-link>
      <router-link v-if="!isAuthenticated" :to="{ name: 'register' }">Register</router-link>
      <router-link v-if="isAuthenticated" :to="{ name: 'user-account' }">Account Settings</router-link>
    </nav>

    <div class="welcome-section">
      <h1>Welcome to Your Todo Manager</h1>
      <p v-if="isAuthenticated">
        Manage tasks, keep your streak alive and review deadlines in calendar view.
      </p>
      <p v-else>Please log in to track your todos and see your statistics.</p>
    </div>

    <div v-if="isAuthenticated" class="stats-section">
      <h2>Your Statistics</h2>
      <p>Current Streak: {{ user.current_streak ?? 0 }}</p>
      <p>Longest Streak: {{ user.longest_streak ?? 0 }}</p>
      <p>Pomodoro Sessions: {{ user.pomodoro_sessions ?? 0 }}</p>
      <p>Tasks Completed: {{ user.tasks_completed ?? 0 }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";

import { useAuthStore } from "../store";

const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user ?? {});

onMounted(() => {
  authStore.fetchUser();
});
</script>

<style scoped>
* {
  font-family: Andale Mono, monospace;
}

.container {
  max-width: 800px;
  margin: 20px auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.nav-bar {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px;
  background: #007bff;
  border-radius: 6px;
}

.nav-bar a {
  text-decoration: none;
  color: white;
  font-weight: bold;
  transition: opacity 0.3s ease;
}

.nav-bar a:hover {
  opacity: 0.8;
}

.welcome-section {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-top: 20px;
}

.welcome-section h1 {
  font-size: 24px;
  color: #222;
}

.welcome-section p {
  font-size: 16px;
  color: #555;
}

.stats-section {
  padding: 20px;
  background: #ffffff;
  border-radius: 6px;
  margin-top: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.stats-section h2 {
  font-size: 20px;
  color: #222;
  margin-bottom: 10px;
}

.stats-section p {
  font-size: 16px;
  color: #555;
  margin: 6px 0;
}
</style>
