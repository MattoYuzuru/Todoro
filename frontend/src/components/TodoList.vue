<template>
  <div>
    <div class="container">
      <h2>Your ToDos</h2>
      <ul v-if="todos.length" class="list-group mt-4">
        <li
          v-for="todo in todos"
          :key="todo.id"
          :class="['list-group-item', { 'completed-todo': todo.status === 'Completed' }]"
        >
          <router-link :to="{ name: 'todo-details', params: { id: todo.id } }" class="todo-link">
            <span class="todo-title">{{ todo.title }}</span><br>
            <span class="todo-description">{{ todo.description }}</span>
          </router-link>
          <div class="button-group">
            <button v-if="todo.status !== 'Completed'" @click="markCompleted(todo.id)" class="complete-btn">
              Complete
            </button>
            <button @click="deleteTodo(todo.id)">Delete</button>
          </div>
        </li>
        <div class="pagination">
          <button @click="prevPage" :disabled="currentPage === 1">Previous</button>
          <span>Page {{ currentPage }}</span>
          <button @click="nextPage" :disabled="todos.length < limit">Next</button>
        </div>
      </ul>
      <p v-else class="no-todos">{{ loading ? "Loading..." : "There are no todos yet." }}</p>
    </div>
    <div class="create-button-container">
      <router-link :to="{ name: 'create-todo' }">
        <button class="all-button">Add New Todo</button>
      </router-link>
      <router-link :to="{ name: 'home' }">
        <button class="all-button">Home Page</button>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import api from "../api/client";
import { useAuthStore } from "../store";

const authStore = useAuthStore();
const router = useRouter();

const todos = ref([]);
const currentPage = ref(1);
const limit = 10;
const loading = ref(false);

async function ensureAuth() {
  if (!authStore.isAuthenticated) {
    await authStore.fetchUser();
  }
  if (!authStore.isAuthenticated) {
    await router.push({ name: "login" });
    return false;
  }
  return true;
}

async function fetchTodos() {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * limit;
    const response = await api.get(`/todos/all/?skip=${skip}&limit=${limit}`);
    todos.value = response.data;
  } catch (error) {
    console.error("Не удалось загрузить задачи:", error);
  } finally {
    loading.value = false;
  }
}

async function deleteTodo(todoId) {
  try {
    await api.delete(`/todos/${todoId}`);
    await fetchTodos();
  } catch (error) {
    console.error("Не удалось удалить задачу:", error);
  }
}

async function markCompleted(todoId) {
  try {
    await api.post(`/todos/${todoId}/complete`);
    await authStore.fetchUser();
    await fetchTodos();
  } catch (error) {
    console.error("Не удалось отметить задачу выполненной:", error);
  }
}

async function nextPage() {
  currentPage.value += 1;
  await fetchTodos();
}

async function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value -= 1;
    await fetchTodos();
  }
}

onMounted(async () => {
  const canContinue = await ensureAuth();
  if (canContinue) {
    await fetchTodos();
  }
});
</script>

<style scoped>
* {
  font-family: Andale Mono, monospace;
}

.container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
}

.list-group {
  list-style: none;
  padding: 0;
}

.list-group-item {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  transition: background-color 0.2s ease-in-out;
}

.list-group-item:hover {
  background-color: #f9f9f9;
}

.completed-todo {
  border-color: #4caf50;
  background-color: #e8f5e9;
}

.todo-link {
  text-decoration: none;
  color: #333;
  flex-grow: 1;
  font-weight: 500;
}

.todo-link:hover {
  text-decoration: underline;
}

.todo-title {
  font-size: 18px;
  font-weight: bold;
  color: #212121;
}

.todo-description {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.button-group {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

button {
  padding: 8px 14px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease-in-out;
}

.complete-btn {
  background-color: #4caf50;
  color: white;
}

.complete-btn:hover {
  background-color: #388e3c;
}

button:nth-child(2) {
  background-color: #f44336;
  color: white;
}

button:nth-child(2):hover {
  background-color: #d32f2f;
}

button:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.pagination button {
  background-color: #007bff;
  color: white;
}

.pagination button:hover {
  background-color: #0056b3;
}

.create-button-container {
  text-align: center;
  margin-top: 20px;
}

.all-button {
  margin: 2px;
  display: inline-block;
  padding: 10px 20px;
  background-color: #4caf50;
  color: white;
  font-size: 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.all-button:hover {
  background-color: #388e3c;
}

.no-todos {
  text-align: center;
  margin-top: 20px;
  font-size: 18px;
  color: #757575;
}
</style>
