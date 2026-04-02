<template>
  <div class="calendar-container">
    <div class="calendar-header">
      <div>
        <h1>Calendar</h1>
        <p>Tasks are grouped by due date for the selected month.</p>
      </div>
      <input v-model="selectedMonth" type="month" class="month-picker">
    </div>

    <div v-if="groupedTodos.length" class="day-groups">
      <article v-for="group in groupedTodos" :key="group.date" class="day-group">
        <div class="group-header">
          <div>
            <h2>{{ formatDate(group.date) }}</h2>
            <p>{{ group.items.length }} task(s)</p>
          </div>
          <router-link :to="{ name: 'calendar-day', params: { date: group.date } }" class="view-link">
            Open day
          </router-link>
        </div>

        <ul>
          <li v-for="todo in group.items" :key="todo.id">
            <router-link :to="{ name: 'todo-details', params: { id: todo.id } }">
              {{ todo.title }}
            </router-link>
            <span :class="['status-badge', todo.status.toLowerCase().replace(/\s+/g, '-')]">
              {{ todo.status }}
            </span>
          </li>
        </ul>
      </article>
    </div>

    <div v-else class="empty-state">
      <p>No tasks with due dates found for this month.</p>
      <router-link :to="{ name: 'create-todo' }" class="view-link">Create task</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import api from "../api/client";
import { useAuthStore } from "../store";

const authStore = useAuthStore();
const router = useRouter();

const todos = ref([]);
const selectedMonth = ref(new Date().toISOString().slice(0, 7));

const groupedTodos = computed(() => {
  const groups = new Map();

  todos.value
    .filter((todo) => todo.due_date && todo.due_date.startsWith(selectedMonth.value))
    .sort((left, right) => left.due_date.localeCompare(right.due_date))
    .forEach((todo) => {
      const group = groups.get(todo.due_date) ?? [];
      group.push(todo);
      groups.set(todo.due_date, group);
    });

  return Array.from(groups.entries()).map(([date, items]) => ({ date, items }));
});

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString();
}

async function fetchTodos() {
  try {
    const response = await api.get("/todos/all/?skip=0&limit=100");
    todos.value = response.data;
  } catch (error) {
    console.error("Не удалось загрузить календарные данные:", error);
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
.calendar-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.month-picker {
  padding: 10px 12px;
  border: 1px solid #d0d7e2;
  border-radius: 8px;
}

.day-groups {
  display: grid;
  gap: 16px;
}

.day-group {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #ddd;
  padding: 16px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.day-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.day-group li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.day-group li:last-child {
  border-bottom: 0;
}

.view-link {
  display: inline-block;
  padding: 8px 16px;
  background-color: #2196f3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.view-link:hover {
  background-color: #0b7dda;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.pending,
.status-badge.in-progress,
.status-badge.postponed {
  background: #eef4ff;
  color: #255bb5;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #2f7d32;
}

.empty-state {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #ddd;
}
</style>
