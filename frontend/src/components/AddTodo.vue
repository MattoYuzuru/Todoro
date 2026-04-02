<template>
  <div class="add-todo">
    <h2>Create New Todo</h2>
    <form @submit.prevent="createTodo">
      <label>Title:</label>
      <input v-model="todo.title" required>

      <label>Description:</label>
      <textarea v-model="todo.description" />

      <label>Status:</label>
      <select v-model="todo.status">
        <option value="Pending">Pending</option>
        <option value="Postponed">Postponed</option>
        <option value="In Progress">In Progress</option>
        <option value="Completed">Completed</option>
      </select>

      <label>Priority:</label>
      <select v-model="todo.priority">
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
      </select>

      <label>Due Date:</label>
      <input type="date" v-model="todo.due_date">

      <button type="submit" class="submit-btn">Create Todo</button>
      <router-link :to="{ name: 'home' }">
        <button type="button" class="home-btn">Home Page</button>
      </router-link>
    </form>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";

import api from "../api/client";
import { useAuthStore } from "../store";

const authStore = useAuthStore();
const router = useRouter();

const todo = reactive({
  title: "",
  description: "",
  status: "Pending",
  priority: "Medium",
  due_date: "",
});

if (!authStore.isAuthenticated) {
  router.push({ name: "login" });
}

async function createTodo() {
  try {
    await api.post("/todos/", {
      ...todo,
      due_date: todo.due_date || null,
    });
    await router.push({ name: "todo-list" });
  } catch (error) {
    console.error("Не удалось создать задачу:", error.response?.data ?? error);
  }
}
</script>

<style scoped>
* {
  font-family: Andale Mono, monospace;
}

.add-todo {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  font-size: 22px;
  color: #222;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-top: 12px;
  font-size: 14px;
  color: #333;
}

input,
textarea,
select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 16px;
  margin-top: 5px;
  box-sizing: border-box;
  width: 100%;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  margin-top: 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.home-btn {
  width: 100%;
  padding: 12px;
  margin-top: 20px;
  background: #b9b9b9;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.submit-btn:hover {
  background: #0056b3;
}

.home-btn:hover {
  background: #929292;
}
</style>
