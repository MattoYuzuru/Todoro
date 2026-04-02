<template>
  <TransitionGroup name="dock" tag="aside" class="timer-dock">
    <article
      v-for="timer in activeTimers"
      :key="timer.todoId"
      class="timer-dock__card"
    >
      <div class="timer-dock__header">
        <div>
          <p class="eyebrow">{{ timer.detached ? "Сохраненная сессия" : "Активная сессия" }}</p>
          <h3>{{ timer.title }}</h3>
        </div>
        <button
          class="icon-button"
          :disabled="timer.isRunning"
          @click="dismiss(timer.todoId)"
        >
          ×
        </button>
      </div>

      <div class="timer-dock__time">
        {{ formatDuration(timer.elapsedTime) }}
      </div>

      <div class="task-card__meta">
        <span class="chip" :data-tone="timer.detached ? 'danger' : timer.isRunning ? 'accent' : 'muted'">
          {{ timer.detached ? "Задача удалена" : timer.isRunning ? "Фокус идет" : "На паузе" }}
        </span>
        <span v-if="timer.priority" class="chip" data-tone="priority">
          {{ getPriorityLabel(timer.priority) }}
        </span>
        <span v-if="timer.dueDate" class="chip" :data-tone="isOverdue(timer.dueDate) ? 'danger' : 'calm'">
          {{ formatDateLabel(timer.dueDate) }}
        </span>
      </div>

      <div class="timer-dock__actions">
        <button v-if="!timer.detached" class="button button--accent" @click="toggleTimer(timer)">
          {{ timer.isRunning ? "Пауза" : "Продолжить" }}
        </button>
        <button v-if="!timer.detached" class="button button--ghost" @click="finishTimer(timer.todoId)">
          Завершить
        </button>
        <RouterLink
          v-if="!timer.detached"
          class="button button--ghost"
          :to="{ name: 'todo-details', params: { id: timer.todoId } }"
        >
          Открыть
        </RouterLink>
        <button v-if="timer.detached" class="button button--ghost" @click="dismiss(timer.todoId)">
          Скрыть
        </button>
      </div>
    </article>
  </TransitionGroup>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { useTimerStore } from "../store";
import { formatDateLabel, formatDuration, getPriorityLabel, isOverdue } from "../utils/formatters";

const timerStore = useTimerStore();

const activeTimers = computed(() => timerStore.activeTimers);

async function toggleTimer(timer) {
  try {
    if (timer.isRunning) {
      await timerStore.pauseTimer(timer.todoId);
      return;
    }

    await timerStore.startTimer({
      id: timer.todoId,
      title: timer.title,
      priority: timer.priority,
      due_date: timer.dueDate,
      status: timer.status,
    });
  } catch (error) {
    console.error("Не удалось переключить таймер:", error);
  }
}

async function finishTimer(todoId) {
  try {
    await timerStore.finishTimer(todoId);
  } catch (error) {
    console.error("Не удалось завершить таймер:", error);
  }
}

function dismiss(todoId) {
  timerStore.dismissTimer(todoId);
}
</script>
