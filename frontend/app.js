const state = {
  token: localStorage.getItem("agent_ticket_token") || "",
  customerId: localStorage.getItem("agent_ticket_customer_id") || "",
  ticketId: localStorage.getItem("agent_ticket_ticket_id") || "",
};

const el = (id) => document.getElementById(id);

function init() {
  el("token").value = state.token;
  el("customerId").value = state.customerId;
  el("ticketId").value = state.ticketId;

  el("healthButton").addEventListener("click", testarHealth);
  el("registerButton").addEventListener("click", registrar);
  el("loginButton").addEventListener("click", login);
  el("createCustomerButton").addEventListener("click", criarCustomer);
  el("listCustomersButton").addEventListener("click", listarCustomers);
  el("chatButton").addEventListener("click", enviarChat);
  el("getTicketButton").addEventListener("click", buscarTicket);
  el("token").addEventListener("input", salvarTokenManual);
}

async function api(path, options = {}) {
  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  const token = el("token").value.trim();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`/api${path}`, {
    ...options,
    headers,
  });
  const text = await response.text();
  const data = parseJson(text);

  mostrarResposta({
    status: response.status,
    ok: response.ok,
    data,
  });

  if (!response.ok) {
    throw new Error(typeof data?.detail === "string" ? data.detail : "Erro na API.");
  }

  return data;
}

function parseJson(text) {
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function mostrarResposta(payload) {
  el("output").textContent = JSON.stringify(payload, null, 2);
}

function salvarTokenManual() {
  state.token = el("token").value.trim();
  localStorage.setItem("agent_ticket_token", state.token);
}

function salvarToken(data) {
  if (!data?.access_token) {
    return;
  }

  state.token = data.access_token;
  el("token").value = data.access_token;
  localStorage.setItem("agent_ticket_token", data.access_token);
}

function salvarCustomerId(customerId) {
  if (!customerId) {
    return;
  }

  state.customerId = customerId;
  el("customerId").value = customerId;
  localStorage.setItem("agent_ticket_customer_id", customerId);
}

function salvarTicketId(ticketId) {
  if (!ticketId) {
    return;
  }

  state.ticketId = ticketId;
  el("ticketId").value = ticketId;
  localStorage.setItem("agent_ticket_ticket_id", ticketId);
}

async function testarHealth() {
  await api("/health");
}

async function registrar() {
  const data = await api("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      name: el("authName").value,
      email: el("authEmail").value,
      password: el("authPassword").value,
      role: el("authRole").value,
    }),
  });
  salvarToken(data);
}

async function login() {
  const data = await api("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email: el("authEmail").value,
      password: el("authPassword").value,
    }),
  });
  salvarToken(data);
}

async function criarCustomer() {
  const data = await api("/customers", {
    method: "POST",
    body: JSON.stringify({
      name: el("customerName").value,
      email: el("customerEmail").value,
      phone: el("customerPhone").value,
      document: el("customerDocument").value,
    }),
  });
  salvarCustomerId(data?.id);
}

async function listarCustomers() {
  const data = await api("/customers");
  if (Array.isArray(data) && data[0]?.id && !el("customerId").value.trim()) {
    salvarCustomerId(data[0].id);
  }
}

async function enviarChat() {
  const ticketId = el("ticketId").value.trim();
  const payload = {
    mensagem: el("chatMessage").value,
    customer_id: el("customerId").value.trim(),
    top_k: Number(el("topK").value || 3),
    provedor_ia: el("provider").value,
  };

  if (ticketId) {
    payload.ticket_id = ticketId;
  }

  const data = await api("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  salvarTicketId(data?.ticket_id);
}

async function buscarTicket() {
  const ticketId = el("ticketId").value.trim();
  if (!ticketId) {
    mostrarResposta({ ok: false, detail: "Informe um ticket_id." });
    return;
  }

  await api(`/tickets/${ticketId}`);
}

init();
