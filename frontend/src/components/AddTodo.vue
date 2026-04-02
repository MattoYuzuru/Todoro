<template>
  <section class="page-shell">
    <section class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Новая задача</p>
          <h1 style="margin: 0; font-size: 2.4rem; letter-spacing: -0.05em;">Собери задачу так, чтобы ее хотелось взять в работу сразу</h1>
        </div>
      </div>
    </section>

    <div class="composer-grid">
      <section class="panel">
        <form class="form-grid" @submit.prevent="createTodo">
          <div class="field-block">
            <label for="title">Заголовок</label>
            <input id="title" v-model="todo.title" class="field" required placeholder="Например, подготовить демо-экран для клиента">
          </div>

          <div class="field-block">
            <label for="description">Описание</label>
            <textarea
              id="description"
              v-model="todo.description"
              class="textarea"
              placeholder="Добавь критерии готовности, контекст или шаги."
            />
          </div>

          <div class="form-grid form-grid--two">
            <div class="field-block">
              <label for="status">Статус</label>
              <select id="status" v-model="todo.status" class="select">
                <option value="Pending">В очереди</option>
                <option value="In Progress">В работе</option>
                <option value="Postponed">Отложена</option>
                <option value="Completed">Завершена</option>
              </select>
            </div>

            <div class="field-block">
              <label for="priority">Приоритет</label>
              <select id="priority" v-model="todo.priority" class="select">
                <option value="">Без приоритета</option>
                <option value="Low">Низкий</option>
                <option value="Medium">Средний</option>
                <option value="High">Высокий</option>
              </select>
            </div>
          </div>

          <div class="field-block">
            <label for="due-date">Дедлайн</label>
            <input id="due-date" v-model="todo.due_date" class="field" type="date">
          </div>

          <div class="toolbar-row">
            <div class="inline-actions">
              <button class="button button--ghost" type="button" @click="applyPreset('today')">
                Дедлайн сегодня
              </button>
              <button class="button button--ghost" type="button" @click="applyPreset('focus')">
                Быстрый фокус
              </button>
              <button class="button button--ghost" type="button" @click="applyPreset('deep')">
                Глубокая работа
              </button>
            </div>
          </div>

          <div class="inline-actions">
            <button class="button button--accent" type="submit">
              Создать и открыть
            </button>
            <RouterLink class="button button--ghost" :to="{ name: 'todo-list' }">
              Отмена
            </RouterLink>
          </div>
        </form>
      </section>

      <aside class="panel sticky-panel">
        <p class="eyebrow">Preview</p>
        <div class="spotlight-card">
          <div class="task-card__meta">
            <span class="chip" :data-tone="statusTone">{{ todo.status }}</span>
            <span class="chip" data-tone="priority">{{ todo.priority || "Без приоритета" }}</span>
            <span class="chip" :data-tone="todo.due_date ? 'calm' : 'muted'">
              {{ todo.due_date || "Без дедлайна" }}
            </span>
          </div>

          <h3>{{ todo.title || "Новая задача без названия" }}</h3>
          <p>{{ todo.description || "Описание пока не добавлено. Хорошая задача обычно объясняет, что именно должно появиться на выходе." }}</p>

          <div class="mini-stat">
            <span>Следующий шаг после создания</span>
            <strong>{{ nextStepText }}</strong>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { useAuthStore, useTodoStore } from "../store";

const authStore = useAuthStore();
const todoStore = useTodoStore();
const router = useRouter();

const todo = reactive({
  title: "",
  description: "",
  status: "Pending",
  priority: "Medium",
  due_date: "",
});

const statusTone = computed(() => {
  if (todo.status === "Completed") {
    return "success";
  }
  if (todo.status === "In Progress") {
    return "accent";
  }
  if (todo.status === "Postponed") {
    return "danger";
  }

  return "muted";
});
const nextStepText = computed(() => {
  if (todo.status === "Completed") {
    return "карточка сразу уйдет в завершенные";
  }
  if (todo.status === "In Progress") {
    return "можно сразу запустить таймер";
  }

  return "она появится в рабочей очереди";
});

function applyPreset(type) {
  if (type === "today") {
    todo.due_date = new Date().toISOString().slice(0, 10);
    return;
  }

  if (type === "focus") {
    todo.status = "In Progress";
    todo.priority = "High";
    todo.title = todo.title || "Фокус-сессия";
    return;
  }

  todo.status = "Pending";
  todo.priority = "High";
  todo.description = todo.description || "Разбить задачу на шаги и провести минимум два фокус-раунда.";
}

async function createTodo() {
  try {
    const createdTodo = await todoStore.createTodo({
      ...todo,
      priority: todo.priority || null,
      due_date: todo.due_date || null,
    });

    await router.push({ name: "todo-details", params: { id: createdTodo.id } });
  } catch (error) {
    console.error("Не удалось создать задачу:", error.response?.data ?? error);
  }
}

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.fetchUser();
  }

  if (!authStore.isAuthenticated) {
    await router.push({ name: "login" });
  }
});
</script>
