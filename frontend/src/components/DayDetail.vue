<template>
  <div class="day-detail">
    <div class="header">
      <router-link :to="{ name: 'calendar' }" class="back-btn">
        &larr; Back to Calendar
      </router-link>
      <h1>{{ formattedDate }}</h1>
    </div>

    <div v-if="loading" class="panel">Loading...</div>

    <div v-else-if="todos.length === 0" class="panel">
      <p>No todos for this day.</p>
      <router-link :to="{ name: 'create-todo' }" class="add-todo-btn">
        Create Todo
      </router-link>
    </div>

    <div v-else class="todo-list">
      <article v-for="todo in todos" :key="todo.id" class="todo-item">
        <div>
          <h3>{{ todo.title }}</h3>
          <p>{{ todo.description || "No description" }}</p>
        </div>
        <div class="todo-meta">
          <span>{{ todo.priority || "No priority" }}</span>
          <span>{{ todo.status }}</span>
          <router-link :to="{ name: 'todo-details', params: { id: todo.id } }">Open</router-link>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import api from "../api/client";
import { useAuthStore } from "../store";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const loading = ref(true);
const todos = ref([]);

const dateValue = computed(() => route.params.date);
const formattedDate = computed(() => {
  return new Date(`${dateValue.value}T00:00:00`).toLocaleDateString();
});

async function fetchTodos() {
  try {
    const response = await api.get("/todos/all/?skip=0&limit=100");
    todos.value = response.data.filter((todo) => todo.due_date === dateValue.value);
  } catch (error) {
    console.error("Не удалось загрузить задачи за день:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.fetchUser();
  }
  if (!authStore.isAuthenticated) {
    await router.push({ name: "login" });
    return;
  }
  await fetchTodos();
});
</script>

<style scoped>
.day-detail {
  max-width: 760px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}

.back-btn,
.add-todo-btn {
  color: #0b7dda;
  text-decoration: none;
  font-weight: bold;
}

.panel,
.todo-item {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 16px;
}

.todo-list {
  display: grid;
  gap: 16px;
}

.todo-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}
</style>
