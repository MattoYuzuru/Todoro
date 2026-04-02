<template>
  <article :class="['task-card', { 'task-card--compact': compact }]">
    <div>
      <div class="task-card__meta">
        <span class="chip" :data-tone="statusTone">{{ getStatusLabel(todo.status) }}</span>
        <span v-if="todo.priority" class="chip" data-tone="priority">{{ getPriorityLabel(todo.priority) }}</span>
        <span
          v-if="todo.due_date"
          class="chip"
          :data-tone="isOverdue(todo.due_date) ? 'danger' : 'calm'"
        >
          {{ formatDateLabel(todo.due_date) }}
        </span>
      </div>

      <div class="section-heading" style="margin-top: 16px; margin-bottom: 12px;">
        <div>
          <h3>{{ todo.title }}</h3>
          <p class="micro-copy" style="margin-top: 8px;">
            {{ timerLabel }}
          </p>
        </div>
      </div>

      <p v-if="showDescription">
        {{ todo.description || "Добавь описание, чтобы задача читалась как понятный сценарий, а не как обрывок мысли." }}
      </p>
    </div>

    <div>
      <div class="task-card__stats">
        <div>
          <span>Сессии</span>
          <strong>{{ todo.pomodoro_sessions }}</strong>
        </div>
        <div>
          <span>Время</span>
          <strong>{{ formatDuration(todo.total_time_spent) }}</strong>
        </div>
        <div>
          <span>Серия</span>
          <strong>{{ todo.current_streak }}</strong>
        </div>
      </div>

      <div class="task-actions" style="margin-top: 18px;">
        <button
          v-if="todo.status !== 'Completed' || elapsedTime > 0"
          class="button button--accent"
          @click="toggleTimer"
        >
          {{ timerActionLabel }}
        </button>
        <button
          v-if="elapsedTime > 0"
          class="button button--ghost"
          @click="finishTimer"
        >
          Завершить раунд
        </button>
        <button
          v-if="todo.status !== 'Completed'"
          class="button button--secondary"
          @click="completeTodo"
        >
          Готово
        </button>
        <RouterLink class="button button--ghost" :to="{ name: 'todo-details', params: { id: todo.id } }">
          Открыть
        </RouterLink>
        <button class="button button--danger" @click="deleteTodo">
          Удалить
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { useAuthStore, useTimerStore, useTodoStore } from "../store";
import {
  formatDateLabel,
  formatDuration,
  getPriorityLabel,
  getStatusLabel,
  isOverdue,
} from "../utils/formatters";

const props = defineProps({
  compact: {
    type: Boolean,
    default: false,
  },
  showDescription: {
    type: Boolean,
    default: true,
  },
  todo: {
    type: Object,
    required: true,
  },
});

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();

const timer = computed(() => timerStore.getTimer(props.todo.id));
const elapsedTime = computed(() => timerStore.getElapsedTime(props.todo.id));
const timerActionLabel = computed(() => {
  if (timer.value?.isRunning) {
    return "Пауза";
  }

  return elapsedTime.value > 0 ? "Продолжить" : "Старт";
});
const timerLabel = computed(() => {
  if (timer.value?.isRunning) {
    return `Таймер в эфире · ${formatDuration(elapsedTime.value)}`;
  }

  if (elapsedTime.value > 0) {
    return `Пауза · ${formatDuration(elapsedTime.value)}`;
  }

  return "Таймер еще не запускался";
});
const statusTone = computed(() => {
  if (props.todo.status === "Completed") {
    return "success";
  }
  if (props.todo.status === "Postponed") {
    return "danger";
  }
  if (props.todo.status === "In Progress") {
    return "accent";
  }

  return "muted";
});

async function toggleTimer() {
  try {
    if (timer.value?.isRunning) {
      await timerStore.pauseTimer(props.todo.id);
      return;
    }

    await timerStore.startTimer(props.todo);
  } catch (error) {
    console.error("Не удалось переключить таймер задачи:", error);
  }
}

async function finishTimer() {
  try {
    await timerStore.finishTimer(props.todo.id);
  } catch (error) {
    console.error("Не удалось завершить помидор:", error);
  }
}

async function completeTodo() {
  try {
    const updatedTodo = await todoStore.completeTodo(props.todo.id);
    timerStore.attachTodo(updatedTodo);
    await authStore.fetchUser();
  } catch (error) {
    console.error("Не удалось завершить задачу:", error);
  }
}

async function deleteTodo() {
  try {
    if (elapsedTime.value > 0 || timer.value?.isRunning) {
      timerStore.archiveDeletedTimer(props.todo);
    }
    await todoStore.deleteTodo(props.todo.id);
  } catch (error) {
    console.error("Не удалось удалить задачу:", error);
  }
}
</script>
