<template>
  <section class="page-shell">
    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">День целиком</p>
          <h1 style="margin: 0; font-size: 2.4rem; letter-spacing: -0.05em;">{{ formattedDate }}</h1>
        </div>
        <RouterLink class="button button--ghost" :to="{ name: 'calendar' }">
          Назад к календарю
        </RouterLink>
      </div>

      <div class="mini-stat">
        <span>Найдено задач</span>
        <strong>{{ todos.length }}</strong>
      </div>
    </section>

    <section class="panel">
      <div v-if="todos.length" class="task-grid">
        <TaskCard
          v-for="todo in todos"
          :key="todo.id"
          :todo="todo"
          compact
        />
      </div>
      <div v-else class="empty-state">
        <p>На этот день пока ничего не назначено.</p>
        <RouterLink class="button button--accent" :to="{ name: 'create-todo' }">
          Создать задачу
        </RouterLink>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import TaskCard from "./TaskCard.vue";
import { useAuthStore, useTimerStore, useTodoStore } from "../store";
import { formatDateLabel } from "../utils/formatters";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();
const route = useRoute();
const router = useRouter();

const dateValue = computed(() => String(route.params.date));
const formattedDate = computed(() => formatDateLabel(dateValue.value));
const todos = computed(() => todoStore.sortedTodos.filter((todo) => todo.due_date === dateValue.value));

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.fetchUser();
  }

  if (!authStore.isAuthenticated) {
    await router.push({ name: "login" });
    return;
  }

  const items = await todoStore.fetchTodos({ force: true });
  await timerStore.hydrateForTodos(items);
});
</script>
