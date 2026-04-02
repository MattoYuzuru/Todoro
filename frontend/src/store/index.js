import { computed, ref } from "vue";
import { defineStore } from "pinia";

import api from "../api/client";

function normalizeTodo(todo) {
  if (!todo) {
    return null;
  }

  return {
    ...todo,
    due_date: todo.due_date ? String(todo.due_date).slice(0, 10) : null,
    completed_at: todo.completed_at ?? null,
  };
}

function sortTodos(items) {
  return [...items].sort((left, right) => {
    const leftDate = left.due_date ?? "9999-12-31";
    const rightDate = right.due_date ?? "9999-12-31";

    if (left.status === "Completed" && right.status !== "Completed") {
      return 1;
    }
    if (left.status !== "Completed" && right.status === "Completed") {
      return -1;
    }
    if (leftDate !== rightDate) {
      return leftDate.localeCompare(rightDate);
    }

    return right.updated_at.localeCompare(left.updated_at);
  });
}

let tickHandle = null;
let syncHandle = null;

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("token"));

  const isAuthenticated = computed(() => Boolean(token.value));

  async function fetchUser() {
    if (!token.value) {
      user.value = null;
      return null;
    }

    try {
      const response = await api.get("/users/me/");
      user.value = response.data;
      return user.value;
    } catch (error) {
      console.error("Не удалось получить профиль пользователя:", error);
      logout();
      return null;
    }
  }

  function setToken(value) {
    token.value = value;
    localStorage.setItem("token", value);
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
  }

  return {
    fetchUser,
    isAuthenticated,
    logout,
    setToken,
    token,
    user,
  };
});

export const useTodoStore = defineStore("todos", () => {
  const todos = ref([]);
  const loading = ref(false);
  const loaded = ref(false);

  const sortedTodos = computed(() => sortTodos(todos.value));
  const today = computed(() => new Date().toISOString().slice(0, 10));
  const openTodos = computed(() => sortedTodos.value.filter((todo) => todo.status !== "Completed"));
  const completedTodos = computed(() => sortedTodos.value.filter((todo) => todo.status === "Completed"));
  const dueTodayTodos = computed(() => openTodos.value.filter((todo) => todo.due_date === today.value));
  const overdueTodos = computed(() => openTodos.value.filter((todo) => todo.due_date && todo.due_date < today.value));
  const inProgressTodos = computed(() => openTodos.value.filter((todo) => todo.status === "In Progress"));

  function setTodos(items) {
    todos.value = sortTodos(items.map(normalizeTodo).filter(Boolean));
    loaded.value = true;
  }

  function upsertTodo(todo) {
    const normalized = normalizeTodo(todo);
    if (!normalized) {
      return null;
    }

    const index = todos.value.findIndex((item) => item.id === normalized.id);
    const nextTodos = [...todos.value];

    if (index >= 0) {
      nextTodos.splice(index, 1, normalized);
    } else {
      nextTodos.push(normalized);
    }

    todos.value = sortTodos(nextTodos);
    loaded.value = true;
    return normalized;
  }

  function removeTodo(todoId) {
    todos.value = todos.value.filter((todo) => todo.id !== Number(todoId));
  }

  function getTodoById(todoId) {
    return todos.value.find((todo) => todo.id === Number(todoId)) ?? null;
  }

  async function fetchTodos({ force = false, limit = 100 } = {}) {
    if (loading.value) {
      return todos.value;
    }

    if (loaded.value && !force) {
      return todos.value;
    }

    loading.value = true;
    try {
      const response = await api.get(`/todos/all/?skip=0&limit=${limit}`);
      setTodos(response.data);
      return todos.value;
    } catch (error) {
      console.error("Не удалось загрузить задачи:", error);
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTodo(todoId) {
    const response = await api.get(`/todos/${todoId}`);
    return upsertTodo(response.data);
  }

  async function createTodo(payload) {
    const response = await api.post("/todos/", payload);
    return upsertTodo(response.data.todo);
  }

  async function updateTodo(todoId, payload) {
    const response = await api.put(`/todos/${todoId}`, payload);
    return upsertTodo(response.data);
  }

  async function deleteTodo(todoId) {
    await api.delete(`/todos/${todoId}`);
    removeTodo(todoId);
  }

  async function completeTodo(todoId) {
    const response = await api.post(`/todos/${todoId}/complete`);
    return upsertTodo(response.data.todo);
  }

  function reset() {
    todos.value = [];
    loading.value = false;
    loaded.value = false;
  }

  return {
    completedTodos,
    completeTodo,
    createTodo,
    deleteTodo,
    dueTodayTodos,
    fetchTodo,
    fetchTodos,
    getTodoById,
    inProgressTodos,
    loaded,
    loading,
    openTodos,
    overdueTodos,
    removeTodo,
    reset,
    setTodos,
    sortedTodos,
    todos,
    updateTodo,
    upsertTodo,
  };
});

export const useTimerStore = defineStore("timers", () => {
  const authStore = useAuthStore();
  const todoStore = useTodoStore();

  const timers = ref({});
  const now = ref(Date.now());

  const activeTimers = computed(() =>
    Object.values(timers.value)
      .map((timer) => ({
        ...timer,
        elapsedTime: getElapsedTime(timer.todoId),
      }))
      .filter((timer) => timer.isRunning || timer.accumulatedTime > 0)
      .sort((left, right) => {
        if (left.isRunning !== right.isRunning) {
          return Number(right.isRunning) - Number(left.isRunning);
        }

        return right.elapsedTime - left.elapsedTime;
      })
  );

  function ensureTimer(todoId) {
    return timers.value[todoId] ?? {
      todoId: Number(todoId),
      title: "Без названия",
      priority: null,
      dueDate: null,
      status: "Pending",
      accumulatedTime: 0,
      isRunning: false,
      startedAt: null,
      lastSyncedAt: null,
      detached: false,
    };
  }

  function patchTimer(todoId, patch) {
    timers.value = {
      ...timers.value,
      [todoId]: {
        ...ensureTimer(todoId),
        ...patch,
        todoId: Number(todoId),
      },
    };
    return timers.value[todoId];
  }

  function attachTodo(todo) {
    if (!todo?.id) {
      return null;
    }

    return patchTimer(todo.id, {
      title: todo.title,
      priority: todo.priority,
      dueDate: todo.due_date ?? null,
      status: todo.status,
    });
  }

  function getTimer(todoId) {
    return timers.value[todoId] ?? null;
  }

  function getElapsedTime(todoId) {
    const timer = timers.value[todoId];
    if (!timer) {
      return 0;
    }

    if (timer.isRunning && timer.startedAt) {
      const startedAt = new Date(timer.startedAt).getTime();
      if (!Number.isNaN(startedAt)) {
        return Math.max(0, timer.accumulatedTime + Math.floor((now.value - startedAt) / 1000));
      }
    }

    return timer.accumulatedTime ?? 0;
  }

  async function syncStatus(todoId) {
    try {
      const response = await api.get(`/todos/${todoId}/pomodoro/status`);
      const currentTodo = todoStore.getTodoById(todoId);

      return patchTimer(todoId, {
        title: currentTodo?.title ?? ensureTimer(todoId).title,
        priority: currentTodo?.priority ?? ensureTimer(todoId).priority,
        dueDate: currentTodo?.due_date ?? ensureTimer(todoId).dueDate,
        status: currentTodo?.status ?? ensureTimer(todoId).status,
        accumulatedTime: response.data.accumulated_time ?? response.data.elapsed_time ?? 0,
        isRunning: response.data.is_running,
        startedAt: response.data.started_at ?? null,
        lastSyncedAt: new Date().toISOString(),
        detached: false,
      });
    } catch (error) {
      console.error("Не удалось синхронизировать таймер:", error);
      return null;
    }
  }

  async function hydrateForTodos(items) {
    const candidates = items;
    candidates.forEach(attachTodo);
    await Promise.all(candidates.map((todo) => syncStatus(todo.id)));
  }

  async function startTimer(todo) {
    const sourceTodo = todoStore.getTodoById(todo.id) ?? todo;
    attachTodo(sourceTodo);

    const response = await api.post(`/todos/${todo.id}/pomodoro/start`);
    return patchTimer(todo.id, {
      title: sourceTodo.title,
      priority: sourceTodo.priority,
      dueDate: sourceTodo.due_date ?? null,
      status: sourceTodo.status,
      accumulatedTime: response.data.accumulated_time ?? 0,
      isRunning: true,
      startedAt: response.data.start_time,
      lastSyncedAt: new Date().toISOString(),
      detached: false,
    });
  }

  async function pauseTimer(todoId) {
    const response = await api.post(`/todos/${todoId}/pomodoro/pause`);
    return patchTimer(todoId, {
      accumulatedTime: response.data.elapsed_time ?? 0,
      isRunning: false,
      startedAt: null,
      lastSyncedAt: new Date().toISOString(),
      detached: false,
    });
  }

  async function finishTimer(todoId) {
    await api.post(`/todos/${todoId}/pomodoro/finish`);

    patchTimer(todoId, {
      accumulatedTime: 0,
      isRunning: false,
      startedAt: null,
      lastSyncedAt: new Date().toISOString(),
      detached: false,
    });

    await Promise.allSettled([
      todoStore.fetchTodo(todoId),
      authStore.fetchUser(),
    ]);

    dismissTimer(todoId);
  }

  function dismissTimer(todoId) {
    const timer = timers.value[todoId];
    if (!timer || timer.isRunning) {
      return;
    }

    removeTimer(todoId);
  }

  function removeTimer(todoId) {
    if (!timers.value[todoId]) {
      return;
    }

    const nextTimers = { ...timers.value };
    delete nextTimers[todoId];
    timers.value = nextTimers;
  }

  async function syncActiveTimers() {
    const runningIds = Object.values(timers.value)
      .filter((timer) => timer.isRunning && !timer.detached)
      .map((timer) => timer.todoId);

    await Promise.all(runningIds.map((todoId) => syncStatus(todoId)));
  }

  function archiveDeletedTimer(todo) {
    if (!todo?.id) {
      return null;
    }

    const elapsedTime = getElapsedTime(todo.id);
    return patchTimer(todo.id, {
      title: todo.title,
      priority: todo.priority,
      dueDate: todo.due_date ?? null,
      status: "Deleted",
      accumulatedTime: elapsedTime,
      isRunning: false,
      startedAt: null,
      lastSyncedAt: new Date().toISOString(),
      detached: true,
    });
  }

  function boot() {
    if (!tickHandle && typeof window !== "undefined") {
      tickHandle = window.setInterval(() => {
        now.value = Date.now();
      }, 1000);
    }

    if (!syncHandle && typeof window !== "undefined") {
      syncHandle = window.setInterval(() => {
        if (authStore.isAuthenticated) {
          syncActiveTimers();
        }
      }, 30000);
    }
  }

  function reset() {
    timers.value = {};
    now.value = Date.now();
  }

  return {
    activeTimers,
    archiveDeletedTimer,
    attachTodo,
    boot,
    dismissTimer,
    finishTimer,
    getElapsedTime,
    getTimer,
    hydrateForTodos,
    pauseTimer,
    removeTimer,
    reset,
    startTimer,
    syncActiveTimers,
    syncStatus,
    timers,
  };
});
