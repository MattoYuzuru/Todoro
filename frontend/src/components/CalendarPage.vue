<template>
  <section class="page-shell">
    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">План по срокам</p>
          <h1 style="margin: 0; font-size: 2.4rem; letter-spacing: -0.05em;">Календарь, который показывает не только дату, но и плотность нагрузки</h1>
        </div>
        <input v-model="selectedMonth" class="field" type="month" style="max-width: 220px;">
      </div>

      <div class="mini-stat">
        <span>Активный период</span>
        <strong>{{ formatMonthLabel(selectedMonth) }}</strong>
      </div>
    </section>

    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Date clusters</p>
          <h2>Собранные по дням точки напряжения</h2>
        </div>
      </div>

      <div v-if="groupedTodos.length" class="calendar-grid">
        <article v-for="group in groupedTodos" :key="group.date" class="calendar-day-card">
          <div class="task-card__meta">
            <span class="chip" :data-tone="group.isOverdue ? 'danger' : 'calm'">
              {{ formatDateLabel(group.date) }}
            </span>
            <span class="chip" data-tone="muted">{{ group.items.length }} задач</span>
          </div>

          <h3>{{ group.headline }}</h3>
          <p class="muted-copy">{{ group.summary }}</p>

          <div class="form-grid">
            <div
              v-for="todo in group.items.slice(0, 3)"
              :key="todo.id"
              class="mini-stat"
            >
              <span>{{ todo.status }}</span>
              <strong style="font-size: 1rem;">{{ todo.title }}</strong>
            </div>
          </div>

          <RouterLink class="button button--ghost" :to="{ name: 'calendar-day', params: { date: group.date } }">
            Открыть день
          </RouterLink>
        </article>
      </div>
      <div v-else class="empty-state">
        <p>В выбранном месяце нет задач с дедлайнами. Можно создать новую карточку и сразу увидеть ее на таймлайне.</p>
        <RouterLink class="button button--accent" :to="{ name: 'create-todo' }">
          Создать задачу
        </RouterLink>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useAuthStore, useTimerStore, useTodoStore } from "../store";
import { formatDateLabel, formatMonthLabel, isOverdue } from "../utils/formatters";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();
const router = useRouter();

const selectedMonth = ref(new Date().toISOString().slice(0, 7));

const groupedTodos = computed(() => {
  const groups = new Map();

  todoStore.sortedTodos
    .filter((todo) => todo.due_date && todo.due_date.startsWith(selectedMonth.value))
    .forEach((todo) => {
      const group = groups.get(todo.due_date) ?? [];
      group.push(todo);
      groups.set(todo.due_date, group);
    });

  return Array.from(groups.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([date, items]) => ({
      date,
      items,
      isOverdue: isOverdue(date),
      headline: items[0]?.title ?? "Пул задач",
      summary: `${items.filter((todo) => todo.status !== "Completed").length} активных, ${items.filter((todo) => todo.status === "Completed").length} завершенных.`,
    }));
});

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.fetchUser();
  }

  if (!authStore.isAuthenticated) {
    await router.push({ name: "login" });
    return;
  }

  const todos = await todoStore.fetchTodos({ force: true });
  await timerStore.hydrateForTodos(todos);
});
</script>
