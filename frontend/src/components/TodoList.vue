<template>
  <section class="page-shell">
    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Task radar</p>
          <h1 style="margin: 0; font-size: 2.4rem; letter-spacing: -0.05em;">Все задачи на одной интерактивной сцене</h1>
        </div>
        <RouterLink class="button button--accent" :to="{ name: 'create-todo' }">
          Новая задача
        </RouterLink>
      </div>

      <div class="filter-row">
        <input v-model="search" class="field" type="search" placeholder="Поиск по названию или описанию">
        <select v-model="statusFilter" class="select">
          <option value="all">Все статусы</option>
          <option value="Pending">В очереди</option>
          <option value="In Progress">В работе</option>
          <option value="Postponed">Отложена</option>
          <option value="Completed">Завершена</option>
        </select>
        <select v-model="priorityFilter" class="select">
          <option value="all">Все приоритеты</option>
          <option value="Low">Низкий</option>
          <option value="Medium">Средний</option>
          <option value="High">Высокий</option>
        </select>
      </div>
    </section>

    <section class="lane-grid">
      <article v-for="lane in lanes" :key="lane.title" class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ lane.caption }}</p>
            <h2>{{ lane.title }}</h2>
          </div>
          <div class="pill-counter">
            <span>{{ lane.items.length }}</span>
            задач
          </div>
        </div>

        <div v-if="lane.items.length" class="task-grid">
          <TaskCard
            v-for="todo in lane.items"
            :key="todo.id"
            :todo="todo"
            compact
          />
        </div>
        <div v-else class="empty-state">
          <p>{{ lane.empty }}</p>
        </div>
      </article>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import TaskCard from "./TaskCard.vue";
import { useAuthStore, useTimerStore, useTodoStore } from "../store";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const timerStore = useTimerStore();
const router = useRouter();

const search = ref("");
const statusFilter = ref("all");
const priorityFilter = ref("all");

const filteredTodos = computed(() => {
  const query = search.value.trim().toLowerCase();

  return todoStore.sortedTodos.filter((todo) => {
    const matchesQuery =
      !query ||
      todo.title.toLowerCase().includes(query) ||
      (todo.description ?? "").toLowerCase().includes(query);
    const matchesStatus = statusFilter.value === "all" || todo.status === statusFilter.value;
    const matchesPriority = priorityFilter.value === "all" || todo.priority === priorityFilter.value;

    return matchesQuery && matchesStatus && matchesPriority;
  });
});

const lanes = computed(() => [
  {
    title: "В фокусе",
    caption: "активный поток",
    empty: "Нет задач в активной фазе. Запусти работу на любой карточке, и она окажется здесь.",
    items: filteredTodos.value.filter((todo) => todo.status === "In Progress" || timerStore.getElapsedTime(todo.id) > 0),
  },
  {
    title: "Открытые",
    caption: "рабочая очередь",
    empty: "Очередь пуста. Можно создать новую задачу или снять фильтры.",
    items: filteredTodos.value.filter((todo) => ["Pending", "Postponed"].includes(todo.status) && timerStore.getElapsedTime(todo.id) === 0),
  },
  {
    title: "Закрытые",
    caption: "завершенный архив",
    empty: "Здесь пока нет завершенных карточек.",
    items: filteredTodos.value.filter((todo) => todo.status === "Completed"),
  },
]);

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
