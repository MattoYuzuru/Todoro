<template>
  <section class="page-shell">
    <template v-if="isAuthenticated">
      <section class="panel hero-panel">
        <div class="hero-grid">
          <div>
            <p class="eyebrow">Пульт дня</p>
            <h1 class="display-title">Управляй задачами не по страницам, а по реальному состоянию фокуса.</h1>
            <p class="lead-text">
              Интерфейс собран как рабочий пульт: справа видны живые таймеры, на дашборде сразу понятны дедлайны и пробки, а каждую задачу можно запустить из любой точки сайта.
            </p>

            <div class="inline-actions" style="margin-top: 22px;">
              <RouterLink class="button button--accent" :to="{ name: 'create-todo' }">
                Создать задачу
              </RouterLink>
              <RouterLink class="button button--ghost" :to="{ name: 'todo-list' }">
                Открыть все задачи
              </RouterLink>
              <RouterLink class="button button--ghost" :to="{ name: 'calendar' }">
                Смотреть календарь
              </RouterLink>
            </div>
          </div>

          <div class="spotlight-card">
            <p class="eyebrow">Сейчас на панели</p>
            <strong>{{ activeTimers.length }}</strong>
            <p class="lead-text" style="font-size: 0.96rem;">
              {{ spotlightText }}
            </p>
            <div class="mini-stat">
              <span>Сегодня в срок</span>
              <strong>{{ todoStore.dueTodayTodos.length }}</strong>
            </div>
            <div class="mini-stat">
              <span>Просрочено</span>
              <strong>{{ todoStore.overdueTodos.length }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="stats-grid">
        <article class="metric-card">
          <span>Открытые задачи</span>
          <strong>{{ todoStore.openTodos.length }}</strong>
          <p>Показывает актуальную нагрузку по системе.</p>
        </article>
        <article class="metric-card">
          <span>Лучшая серия</span>
          <strong>{{ user.longest_streak ?? 0 }}</strong>
          <p>Хороший индикатор того, насколько ритм устойчив.</p>
        </article>
        <article class="metric-card">
          <span>Pomodoro-сессии</span>
          <strong>{{ user.pomodoro_sessions ?? 0 }}</strong>
          <p>Сколько фокус-раундов уже закрыто системой.</p>
        </article>
        <article class="metric-card">
          <span>Выполнено</span>
          <strong>{{ user.tasks_completed ?? 0 }}</strong>
          <p>Итог полезного выхода, а не просто активности.</p>
        </article>
      </section>

      <section class="content-grid">
        <section class="panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">На сегодня</p>
              <h2>Задачи, которые нельзя потерять из вида</h2>
            </div>
            <RouterLink class="button button--ghost" :to="{ name: 'todo-list' }">
              Ко всем карточкам
            </RouterLink>
          </div>

          <div v-if="focusTodos.length" class="task-grid">
            <TaskCard
              v-for="todo in focusTodos"
              :key="todo.id"
              :todo="todo"
              compact
            />
          </div>
          <div v-else class="empty-state">
            <p>Пока нечего вытаскивать в приоритетный ряд. Можно создать первую задачу и сразу запустить на ней таймер.</p>
            <RouterLink class="button button--accent" :to="{ name: 'create-todo' }">
              Создать первую задачу
            </RouterLink>
          </div>
        </section>

        <section class="panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Прямо сейчас</p>
              <h2>Активные фокус-сессии</h2>
            </div>
          </div>

          <div v-if="activeTimers.length" class="live-feed-grid">
            <article
              v-for="timer in activeTimers.slice(0, 2)"
              :key="timer.todoId"
              class="spotlight-card spotlight-card--timer"
            >
              <p class="eyebrow">{{ timer.isRunning ? "Фокус идет" : "Пауза" }}</p>
              <h3>{{ timer.title }}</h3>
              <p class="spotlight-card__time">{{ formatDuration(timer.elapsedTime) }}</p>
              <div class="task-card__meta">
                <span class="chip" :data-tone="timer.isRunning ? 'accent' : 'muted'">
                  {{ timer.isRunning ? "В работе" : "Остановлено" }}
                </span>
                <span v-if="timer.priority" class="chip" data-tone="priority">
                  {{ getPriorityLabel(timer.priority) }}
                </span>
              </div>
              <RouterLink class="button button--ghost" :to="{ name: 'todo-details', params: { id: timer.todoId } }">
                Открыть задачу
              </RouterLink>
            </article>
          </div>
          <div v-else class="empty-state">
            <p>Боковой стек таймеров пуст. Запусти Pomodoro из карточки задачи, и он сразу появится справа как плавающий контроллер.</p>
          </div>

          <div class="panel panel--dense" style="margin-top: 18px;">
            <p class="eyebrow">Как это работает</p>
            <div class="form-grid">
              <div class="mini-stat">
                <span>1. Выбери задачу</span>
                <strong>из списка, календаря или дашборда</strong>
              </div>
              <div class="mini-stat">
                <span>2. Запусти таймер</span>
                <strong>он всплывет справа и останется доступен везде</strong>
              </div>
              <div class="mini-stat">
                <span>3. Закрой раунд</span>
                <strong>метрики и серия обновятся без переходов</strong>
              </div>
            </div>
          </div>
        </section>
      </section>

      <section class="dashboard-analytics">
        <section class="panel chart-card">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Продуктивность по дням</p>
              <h2>Когда чаще всего закрываются задачи</h2>
            </div>
            <div class="pill-counter">
              <span>{{ peakDay.label }}</span>
              лучший день
            </div>
          </div>

          <div class="bar-chart">
            <div v-for="item in weekdayBars" :key="item.label" class="bar-chart__item">
              <div class="bar-chart__column">
                <div class="bar-chart__fill" :style="{ height: `${item.ratio}%` }"></div>
              </div>
              <strong>{{ item.count }}</strong>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </section>

        <section class="panel chart-card">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Приоритеты</p>
              <h2>Как распределяется основной поток задач</h2>
            </div>
          </div>

          <div class="distribution-list">
            <article v-for="item in priorityBars" :key="item.label" class="distribution-row">
              <div class="distribution-row__head">
                <strong>{{ item.label }}</strong>
                <span>{{ item.count }} шт.</span>
              </div>
              <div class="distribution-row__track">
                <div class="distribution-row__fill" :style="{ width: `${item.ratio}%` }"></div>
              </div>
            </article>
          </div>
        </section>

        <section class="panel chart-card">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Время и результат</p>
              <h2>Сводка по приоритетам и затраченным минутам</h2>
            </div>
            <div class="pill-counter">
              <span>{{ completionRate }}%</span>
              доля завершения
            </div>
          </div>

          <div class="summary-table">
            <div class="summary-table__row summary-table__row--head">
              <span>Приоритет</span>
              <span>Задач</span>
              <span>Готово</span>
              <span>Время</span>
            </div>
            <div v-for="row in timeSummaryRows" :key="row.label" class="summary-table__row">
              <strong>{{ row.label }}</strong>
              <span>{{ row.count }}</span>
              <span>{{ row.completed }}</span>
              <span>{{ row.time }}</span>
            </div>
          </div>
        </section>
      </section>
    </template>

    <template v-else>
      <section class="panel hero-panel">
        <p class="eyebrow">Добро пожаловать</p>
        <h1 class="display-title">Список задач, который выглядит как современный центр управления.</h1>
        <p class="lead-text">
          Здесь задачи не заперты на одной странице. Таймеры всплывают сбоку, календарь дает контекст по срокам, а дашборд показывает весь поток работы без лишних переходов.
        </p>
        <div class="inline-actions" style="margin-top: 22px;">
          <RouterLink class="button button--accent" :to="{ name: 'register' }">
            Начать работу
          </RouterLink>
          <RouterLink class="button button--ghost" :to="{ name: 'login' }">
            Войти
          </RouterLink>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { RouterLink } from "vue-router";

import TaskCard from "./TaskCard.vue";
import { useAuthStore, useTimerStore, useTodoStore } from "../store";
import { formatDuration, getPriorityLabel, getWeekdayLabel } from "../utils/formatters";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user ?? {});
const activeTimers = computed(() => timerStore.activeTimers);
const focusTodos = computed(() => {
  const pool = [
    ...todoStore.dueTodayTodos,
    ...todoStore.inProgressTodos,
    ...todoStore.overdueTodos,
    ...todoStore.openTodos,
  ];

  return [...new Map(pool.map((todo) => [todo.id, todo])).values()].slice(0, 4);
});
const spotlightText = computed(() => {
  if (activeTimers.value.length > 0) {
    return `Главная сессия сейчас на задаче «${activeTimers.value[0].title}». Ее можно приостановить или завершить из бокового блока справа.`;
  }

  return "Пока активных сессий нет. Как только запустишь первый таймер, он появится в боковом стеке и будет доступен по всему сайту.";
});
const weekdayBars = computed(() => {
  const counts = Array.from({ length: 7 }, () => 0);

  todoStore.completedTodos.forEach((todo) => {
    const sourceDate = todo.completed_at ?? todo.updated_at;
    if (!sourceDate) {
      return;
    }

    counts[new Date(sourceDate).getDay()] += 1;
  });

  const maxCount = Math.max(...counts, 1);
  return counts.map((count, index) => ({
    label: getWeekdayLabel(index),
    count,
    ratio: count === 0 ? 8 : Math.max(16, Math.round((count / maxCount) * 100)),
  }));
});
const peakDay = computed(() => {
  return weekdayBars.value.reduce(
    (best, item) => (item.count > best.count ? item : best),
    { label: "нет данных", count: 0 }
  );
});
const priorityBars = computed(() => {
  const labels = ["High", "Medium", "Low", null];
  const total = Math.max(todoStore.sortedTodos.length, 1);

  return labels.map((priority) => {
    const items = todoStore.sortedTodos.filter((todo) => (todo.priority ?? null) === priority);
    return {
      label: getPriorityLabel(priority),
      count: items.length,
      ratio: items.length === 0 ? 4 : Math.max(10, Math.round((items.length / total) * 100)),
    };
  });
});
const timeSummaryRows = computed(() => {
  const labels = ["High", "Medium", "Low", null];

  return labels.map((priority) => {
    const items = todoStore.sortedTodos.filter((todo) => (todo.priority ?? null) === priority);
    const totalSeconds = items.reduce((accumulator, todo) => accumulator + (todo.total_time_spent ?? 0), 0);
    const completed = items.filter((todo) => todo.status === "Completed").length;

    return {
      label: getPriorityLabel(priority),
      count: items.length,
      completed,
      time: formatDuration(totalSeconds),
    };
  });
});
const completionRate = computed(() => {
  if (todoStore.sortedTodos.length === 0) {
    return 0;
  }

  return Math.round((todoStore.completedTodos.length / todoStore.sortedTodos.length) * 100);
});

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    return;
  }

  await authStore.fetchUser();
  const todos = await todoStore.fetchTodos();
  await timerStore.hydrateForTodos(todos);
});
</script>
