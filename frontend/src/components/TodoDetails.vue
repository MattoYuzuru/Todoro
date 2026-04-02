<template>
  <div class="todo-details">
    <template v-if="todo">
      <h2>{{ todo.title }}</h2>
      <h4>{{ todo.description }}</h4>

      <div class="todo-info">
        <p><strong>Status:</strong> {{ todo.status }}</p>
        <p><strong>Priority:</strong> {{ todo.priority || "Not set" }}</p>
        <br>
        <p v-if="todo.due_date"><strong>Due Date:</strong> {{ todo.due_date }}</p>
        <p v-if="todo.completed_at"><strong>Completed At:</strong> {{ formattedCompletedAt }}</p>
        <br>
        <p><strong>Pomodoro Sessions:</strong> {{ todo.pomodoro_sessions }}</p>
        <p><strong>Total Time Spent:</strong> {{ formattedTotalTime }}</p>
        <p><strong>Current Streak:</strong> {{ todo.current_streak }} days</p>
      </div>

      <div class="timer">
        <h3>Pomodoro Timer</h3>
        <p class="timer-display">{{ formattedTime }}</p>
        <button @click="startPomodoro" :disabled="isRunning" class="start-btn">Start</button>
        <button @click="pausePomodoro" :disabled="!isRunning" class="pause-btn">Pause</button>
        <button @click="finishPomodoro" :disabled="!isRunning" class="finish-btn">Finish</button>
      </div>

      <button v-if="todo.status !== 'Completed'" @click="markCompleted">Mark as Completed</button>
      <button @click="deleteTodo">Delete</button>
      <div class="navigation-buttons">
        <router-link :to="{ name: 'home' }">
          <button class="all-button">Go back to Menu</button>
        </router-link>
        <router-link :to="{ name: 'todo-list' }">
          <button class="all-button">Go back to Todos</button>
        </router-link>
      </div>
    </template>

    <p v-else>Loading task...</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import api from "../api/client";
import { useAuthStore } from "../store";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const todo = ref(null);
const timeInSeconds = ref(0);
const isRunning = ref(false);
const accumulatedTime = ref(0);
const startTime = ref(null);

let timerInterval = null;
let statusSyncInterval = null;

const todoId = computed(() => route.params.id);
const formattedTime = computed(() => {
  const minutes = Math.floor(timeInSeconds.value / 60);
  const seconds = timeInSeconds.value % 60;
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
});

const formattedTotalTime = computed(() => {
  const total = todo.value?.total_time_spent ?? 0;
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
});

const formattedCompletedAt = computed(() => {
  return todo.value?.completed_at ? todo.value.completed_at.split("T")[0] : "N/A";
});

function clearTimers() {
  if (timerInterval) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }
  if (statusSyncInterval) {
    window.clearInterval(statusSyncInterval);
    statusSyncInterval = null;
  }
}

function startLocalTimer() {
  if (!startTime.value) {
    startTime.value = new Date(Date.now() - accumulatedTime.value * 1000);
  }

  if (timerInterval) {
    window.clearInterval(timerInterval);
  }

  timerInterval = window.setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime.value.getTime()) / 1000);
    timeInSeconds.value = accumulatedTime.value + elapsed;
    if (timeInSeconds.value >= 1500) {
      finishPomodoro();
    }
  }, 1000);
}

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

async function fetchTodo() {
  try {
    const response = await api.get(`/todos/${todoId.value}`);
    todo.value = response.data;
  } catch (error) {
    console.error("Не удалось загрузить задачу:", error);
  }
}

async function fetchPomodoroTime() {
  try {
    const response = await api.get(`/todos/${todoId.value}/pomodoro/status`);
    timeInSeconds.value = response.data.elapsed_time;
    isRunning.value = response.data.is_running;
    accumulatedTime.value = response.data.accumulated_time ?? 0;
    startTime.value = response.data.started_at ? new Date(response.data.started_at) : null;

    if (isRunning.value) {
      startLocalTimer();
    } else if (timerInterval) {
      window.clearInterval(timerInterval);
      timerInterval = null;
    }
  } catch (error) {
    console.error("Не удалось получить состояние помидора:", error);
  }
}

async function deleteTodo() {
  try {
    await api.delete(`/todos/${todoId.value}`);
    await router.push({ name: "todo-list" });
  } catch (error) {
    console.error("Не удалось удалить задачу:", error);
  }
}

async function markCompleted() {
  try {
    await api.post(`/todos/${todoId.value}/complete`);
    await authStore.fetchUser();
    await fetchTodo();
  } catch (error) {
    console.error("Не удалось завершить задачу:", error);
  }
}

async function startPomodoro() {
  try {
    const response = await api.post(`/todos/${todoId.value}/pomodoro/start`);
    isRunning.value = true;
    startTime.value = new Date(response.data.start_time);
    accumulatedTime.value = response.data.accumulated_time ?? 0;
    timeInSeconds.value = accumulatedTime.value;
    startLocalTimer();
  } catch (error) {
    console.error("Не удалось запустить помидор:", error);
  }
}

async function pausePomodoro() {
  try {
    const response = await api.post(`/todos/${todoId.value}/pomodoro/pause`);
    isRunning.value = false;
    accumulatedTime.value = response.data.elapsed_time;
    timeInSeconds.value = response.data.elapsed_time;
    startTime.value = null;
    if (timerInterval) {
      window.clearInterval(timerInterval);
      timerInterval = null;
    }
    await fetchTodo();
  } catch (error) {
    console.error("Не удалось поставить помидор на паузу:", error);
  }
}

async function finishPomodoro() {
  try {
    await api.post(`/todos/${todoId.value}/pomodoro/finish`);
    isRunning.value = false;
    accumulatedTime.value = 0;
    timeInSeconds.value = 0;
    startTime.value = null;
    if (timerInterval) {
      window.clearInterval(timerInterval);
      timerInterval = null;
    }
    await authStore.fetchUser();
    await fetchTodo();
  } catch (error) {
    console.error("Не удалось завершить помидор:", error);
  }
}

onMounted(async () => {
  const canContinue = await ensureAuth();
  if (!canContinue) {
    return;
  }

  await fetchTodo();
  await fetchPomodoroTime();
  statusSyncInterval = window.setInterval(fetchPomodoroTime, 30000);
});

onBeforeUnmount(() => {
  clearTimers();
});
</script>

<style scoped>
* {
  font-family: Andale Mono, monospace;
}

.todo-details {
  max-width: 600px;
  margin: auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid #ddd;
}

h2 {
  text-align: center;
  margin-bottom: 10px;
}

.todo-info {
  margin: 15px 0;
  font-size: 16px;
}

.todo-info p {
  margin: 6px 0;
  color: #333;
}

.timer {
  text-align: center;
  margin-top: 20px;
}

.timer-display {
  font-size: 24px;
  font-weight: bold;
  color: #222;
  margin: 10px 0;
}

button {
  display: block;
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  transition: background 0.3s ease-in-out;
}

button:disabled {
  background: #b9b9b9;
  cursor: not-allowed;
}

.start-btn {
  background: #28a745;
  color: white;
}

.start-btn:hover {
  background: #218838;
}

.pause-btn {
  background: #ffc107;
  color: black;
}

.pause-btn:hover {
  background: #e0a800;
}

.finish-btn {
  background: #dc3545;
  color: white;
}

.finish-btn:hover {
  background: #c82333;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  gap: 12px;
}

.all-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-align: center;
}

.all-button:hover {
  background-color: #0056b3;
}
</style>
