<template>
  <section v-if="todo" class="page-shell">
    <div class="details-grid">
      <section class="panel focus-stage">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Фокус-сцена</p>
            <h1 style="margin: 0; font-size: 2.8rem; letter-spacing: -0.06em;">{{ todo.title }}</h1>
          </div>
          <div class="task-card__meta">
            <span class="chip" :data-tone="statusTone">{{ getStatusLabel(todo.status) }}</span>
            <span v-if="todo.priority" class="chip" data-tone="priority">{{ getPriorityLabel(todo.priority) }}</span>
          </div>
        </div>

        <p class="lead-text" style="max-width: none;">
          {{ todo.description || "Описание пока пустое. Можно дополнить справа и превратить карточку в полноценный сценарий работы." }}
        </p>

        <div class="timer-hero" style="margin-top: 24px;">
          <div :class="['timer-orbit', { 'timer-orbit--running': timer?.isRunning }]" :style="orbitStyle">
            <strong class="timer-hero__time">{{ formattedElapsed }}</strong>
          </div>

          <div class="task-card__meta">
            <span class="chip" :data-tone="timer?.isRunning ? 'accent' : 'muted'">
              {{ timer?.isRunning ? "Таймер идет" : "Таймер остановлен" }}
            </span>
            <span class="chip" :data-tone="todo.due_date && isOverdue(todo.due_date) ? 'danger' : 'calm'">
              {{ formatDateLabel(todo.due_date) }}
            </span>
            <span class="chip" data-tone="muted">Всего {{ formatDuration(todo.total_time_spent) }}</span>
          </div>

          <div class="inline-actions">
            <button
              class="button button--accent"
              :disabled="timer?.isRunning || todo.status === 'Completed'"
              @click="startTimer"
            >
              Старт
            </button>
            <button class="button button--ghost" :disabled="!timer?.isRunning" @click="pauseTimer">
              Пауза
            </button>
            <button class="button button--secondary" :disabled="elapsedTime === 0" @click="finishTimer">
              Завершить раунд
            </button>
          </div>
        </div>

        <div class="stats-grid" style="margin-top: 24px;">
          <article class="metric-card">
            <span>Pomodoro</span>
            <strong>{{ todo.pomodoro_sessions }}</strong>
            <p>Количество завершенных фокус-раундов.</p>
          </article>
          <article class="metric-card">
            <span>Текущая серия</span>
            <strong>{{ todo.current_streak }}</strong>
            <p>Локальная серия активности по задаче.</p>
          </article>
          <article class="metric-card">
            <span>Завершена</span>
            <strong style="font-size: 1.4rem;">{{ formatDateTime(todo.completed_at) }}</strong>
            <p>Время последнего закрытия задачи.</p>
          </article>
          <article class="metric-card">
            <span>Обновлена</span>
            <strong style="font-size: 1.4rem;">{{ formatDateTime(todo.updated_at) }}</strong>
            <p>Когда карточка менялась в последний раз.</p>
          </article>
        </div>
      </section>

      <aside class="panel sticky-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Редактирование</p>
            <h2>Правь контекст без ухода со сцены</h2>
          </div>
        </div>

        <form class="form-grid" @submit.prevent="saveTodo">
          <div class="field-block">
            <label for="title">Заголовок</label>
            <input id="title" v-model="draft.title" class="field" required>
          </div>

          <div class="field-block">
            <label for="description">Описание</label>
            <textarea id="description" v-model="draft.description" class="textarea" />
          </div>

          <div class="form-grid form-grid--two">
            <div class="field-block">
              <label for="status">Статус</label>
              <select id="status" v-model="draft.status" class="select">
                <option value="Pending">В очереди</option>
                <option value="In Progress">В работе</option>
                <option value="Postponed">Отложена</option>
                <option value="Completed">Завершена</option>
              </select>
            </div>

            <div class="field-block">
              <label for="priority">Приоритет</label>
              <select id="priority" v-model="draft.priority" class="select">
                <option value="">Без приоритета</option>
                <option value="Low">Низкий</option>
                <option value="Medium">Средний</option>
                <option value="High">Высокий</option>
              </select>
            </div>
          </div>

          <div class="field-block">
            <label for="due-date">Дедлайн</label>
            <input id="due-date" v-model="draft.due_date" class="field" type="date">
          </div>

          <div class="inline-actions">
            <button class="button button--accent" type="submit">
              Сохранить
            </button>
            <button
              v-if="todo.status !== 'Completed'"
              class="button button--secondary"
              type="button"
              @click="completeTodo"
            >
              Завершить задачу
            </button>
            <button class="button button--danger" type="button" @click="deleteTodo">
              Удалить
            </button>
          </div>
        </form>
      </aside>
    </div>
  </section>

  <section v-else class="page-shell">
    <div class="panel empty-state">
      <p>Загружаю карточку задачи...</p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore, useTimerStore, useTodoStore } from "../store";
import {
  formatDateLabel,
  formatDateTime,
  formatDuration,
  getPriorityLabel,
  getStatusLabel,
  isOverdue,
} from "../utils/formatters";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();
const route = useRoute();
const router = useRouter();

const draft = reactive({
  title: "",
  description: "",
  status: "Pending",
  priority: "",
  due_date: "",
});

const todoId = computed(() => Number(route.params.id));
const todo = computed(() => todoStore.getTodoById(todoId.value));
const timer = computed(() => timerStore.getTimer(todoId.value));
const elapsedTime = computed(() => timerStore.getElapsedTime(todoId.value));
const formattedElapsed = computed(() => formatDuration(elapsedTime.value));
const orbitProgress = computed(() => Math.min(elapsedTime.value / 1500, 1));
const orbitStyle = computed(() => ({
  "--progress": orbitProgress.value,
  "--progress-angle": `${orbitProgress.value * 360}deg`,
}));
const statusTone = computed(() => {
  if (todo.value?.status === "Completed") {
    return "success";
  }
  if (todo.value?.status === "In Progress") {
    return "accent";
  }
  if (todo.value?.status === "Postponed") {
    return "danger";
  }

  return "muted";
});

watch(
  todo,
  (value) => {
    if (!value) {
      return;
    }

    draft.title = value.title;
    draft.description = value.description ?? "";
    draft.status = value.status;
    draft.priority = value.priority ?? "";
    draft.due_date = value.due_date ?? "";
    timerStore.attachTodo(value);
  },
  { immediate: true }
);

async function loadTodo() {
  await todoStore.fetchTodo(todoId.value);
  await timerStore.syncStatus(todoId.value);
}

async function saveTodo() {
  try {
    const updatedTodo = await todoStore.updateTodo(todoId.value, {
      ...draft,
      priority: draft.priority || null,
      due_date: draft.due_date || null,
    });

    timerStore.attachTodo(updatedTodo);
  } catch (error) {
    console.error("Не удалось сохранить задачу:", error);
  }
}

async function startTimer() {
  try {
    await timerStore.startTimer(todo.value);
  } catch (error) {
    console.error("Не удалось запустить таймер:", error);
  }
}

async function pauseTimer() {
  try {
    await timerStore.pauseTimer(todoId.value);
  } catch (error) {
    console.error("Не удалось поставить таймер на паузу:", error);
  }
}

async function finishTimer() {
  try {
    await timerStore.finishTimer(todoId.value);
    await loadTodo();
  } catch (error) {
    console.error("Не удалось завершить раунд:", error);
  }
}

async function completeTodo() {
  try {
    const updatedTodo = await todoStore.completeTodo(todoId.value);
    timerStore.attachTodo(updatedTodo);
    await authStore.fetchUser();
  } catch (error) {
    console.error("Не удалось завершить задачу:", error);
  }
}

async function deleteTodo() {
  try {
    if (elapsedTime.value > 0 || timer.value?.isRunning) {
      timerStore.archiveDeletedTimer(todo.value);
    }
    await todoStore.deleteTodo(todoId.value);
    await router.push({ name: "todo-list" });
  } catch (error) {
    console.error("Не удалось удалить задачу:", error);
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

  await loadTodo();
});
</script>
