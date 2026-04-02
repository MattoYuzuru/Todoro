const STATUS_LABELS = {
  Pending: "В очереди",
  Postponed: "Отложена",
  "In Progress": "В работе",
  Completed: "Завершена",
  Deleted: "Удалена",
};

const PRIORITY_LABELS = {
  Low: "Низкий",
  Medium: "Средний",
  High: "Высокий",
};

export function formatDuration(totalSeconds = 0) {
  const safeSeconds = Math.max(0, Number(totalSeconds) || 0);
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const seconds = safeSeconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }

  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

export function formatDateLabel(value) {
  if (!value) {
    return "Без дедлайна";
  }

  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    weekday: "short",
  }).format(new Date(`${value}T00:00:00`));
}

export function formatDateTime(value) {
  if (!value) {
    return "Еще не завершена";
  }

  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatMonthLabel(value) {
  if (!value) {
    return "";
  }

  return new Intl.DateTimeFormat("ru-RU", {
    month: "long",
    year: "numeric",
  }).format(new Date(`${value}-01T00:00:00`));
}

export function getStatusLabel(status) {
  return STATUS_LABELS[status] ?? status;
}

export function getPriorityLabel(priority) {
  if (!priority) {
    return "Без приоритета";
  }

  return PRIORITY_LABELS[priority] ?? priority;
}

export function getWeekdayLabel(index) {
  const weekdayLabels = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
  return weekdayLabels[index] ?? "";
}

export function isOverdue(value) {
  if (!value) {
    return false;
  }

  const today = new Date().toISOString().slice(0, 10);
  return value < today;
}
