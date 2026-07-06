const state = {
  token: localStorage.getItem("agent_ticket_token") || "",
  user: parseStoredJson("agent_ticket_user"),
  customer: parseStoredJson("agent_ticket_customer"),
  ticket: parseStoredJson("agent_ticket_ticket"),
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
  el("meButton").addEventListener("click", carregarUsuarioAtual);
  el("createCustomerButton").addEventListener("click", criarCustomer);
  el("listCustomersButton").addEventListener("click", listarCustomers);
  el("chatButton").addEventListener("click", enviarChat);
  el("getTicketButton").addEventListener("click", buscarTicket);
  el("assignMeButton").addEventListener("click", atribuirParaMim);
  el("queueOpenButton").addEventListener("click", () => listarTickets({ status: "open" }));
  el("queuePendingButton").addEventListener("click", () => listarTickets({ status: "pending" }));
  el("queueMineButton").addEventListener("click", listarMinhaFila);
  el("token").addEventListener("input", salvarTokenManual);
  renderEstado();
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

function parseStoredJson(key) {
  const raw = localStorage.getItem(key);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function salvarTokenManual() {
  state.token = el("token").value.trim();
  localStorage.setItem("agent_ticket_token", state.token);

  if (!state.token) {
    state.user = null;
    localStorage.removeItem("agent_ticket_user");
    renderEstado();
  }
}

function salvarToken(data) {
  if (data?.access_token) {
    state.token = data.access_token;
    el("token").value = data.access_token;
    localStorage.setItem("agent_ticket_token", data.access_token);
  }

  if (data?.user) {
    salvarUsuario(data.user);
  }
}

function salvarUsuario(user) {
  if (!user?.id) {
    return;
  }

  state.user = user;
  localStorage.setItem("agent_ticket_user", JSON.stringify(user));
  renderEstado();
}

function salvarCustomer(customer) {
  if (!customer?.id) {
    return;
  }

  state.customer = customer;
  state.customerId = customer.id;
  el("customerId").value = customer.id;
  localStorage.setItem("agent_ticket_customer", JSON.stringify(customer));
  localStorage.setItem("agent_ticket_customer_id", customer.id);
  renderEstado();
}

function salvarCustomerId(customerId) {
  if (!customerId) {
    return;
  }

  state.customerId = customerId;
  el("customerId").value = customerId;
  localStorage.setItem("agent_ticket_customer_id", customerId);
  renderEstado();
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

async function carregarUsuarioAtual() {
  const user = await api("/auth/me");
  salvarUsuario(user);
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
  salvarCustomer(data);
}

async function listarCustomers() {
  const data = await api("/customers");
  if (Array.isArray(data) && data[0]?.id && !el("customerId").value.trim()) {
    salvarCustomer(data[0]);
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
  if (data?.ticket_id) {
    await carregarTicket(data.ticket_id);
  }
}

async function buscarTicket() {
  const ticketId = el("ticketId").value.trim();
  if (!ticketId) {
    mostrarResposta({ ok: false, detail: "Informe um ticket_id." });
    return;
  }

  await carregarTicket(ticketId);
}

async function carregarTicket(ticketId) {
  const ticket = await api(`/tickets/${ticketId}`);
  salvarTicket(ticket);
  return ticket;
}

function salvarTicket(ticket) {
  if (!ticket?.id) {
    return;
  }

  state.ticket = ticket;
  state.ticketId = ticket.id;
  el("ticketId").value = ticket.id;
  localStorage.setItem("agent_ticket_ticket", JSON.stringify(ticket));
  localStorage.setItem("agent_ticket_ticket_id", ticket.id);
  renderEstado();
}

async function atribuirParaMim() {
  const ticketId = el("ticketId").value.trim();
  const userId = state.user?.id;

  if (!ticketId) {
    mostrarResposta({ ok: false, detail: "Informe um ticket_id." });
    return;
  }

  if (!userId) {
    mostrarResposta({ ok: false, detail: "Faca login para carregar seu user_id." });
    return;
  }

  const ticket = await api(`/tickets/${ticketId}/assignment`, {
    method: "PATCH",
    body: JSON.stringify({ assigned_user_id: userId }),
  });
  salvarTicket(ticket);
}

async function listarTickets(filters = {}) {
  const params = new URLSearchParams();

  if (filters.status) {
    params.set("status", filters.status);
  }

  if (filters.assigned_user_id) {
    params.set("assigned_user_id", filters.assigned_user_id);
  }

  await api(`/tickets${params.toString() ? `?${params}` : ""}`);
}

async function listarMinhaFila() {
  if (!state.user?.id) {
    mostrarResposta({ ok: false, detail: "Faca login para carregar seu user_id." });
    return;
  }

  await listarTickets({ assigned_user_id: state.user.id });
}

function renderEstado() {
  const ticket = state.ticket;
  const ultimaMensagemIa = ticket?.messages
    ?.slice()
    .reverse()
    .find((message) => message.sender_type === "ai_agent");
  const metadata = ultimaMensagemIa?.metadata || {};

  el("summaryUser").textContent = state.user
    ? `${state.user.name} (${state.user.role})`
    : "-";
  el("summaryCustomer").textContent = state.customer
    ? `${state.customer.name || state.customer.email} (${state.customer.id})`
    : state.customerId || "-";
  el("summaryTicket").textContent = ticket?.id || state.ticketId || "-";
  el("summaryStatus").textContent = ticket?.status || "-";
  el("summaryCategory").textContent = ticket?.category || "-";
  el("summaryHandoff").textContent = ticket
    ? ticket.requires_human
      ? "sim"
      : "nao"
    : "-";

  el("classificationOutput").textContent = JSON.stringify(
    metadata.classification || ticketClassification(ticket),
    null,
    2,
  );
  el("ragOutput").textContent = JSON.stringify(metadata.rag_docs || [], null, 2);
}

function ticketClassification(ticket) {
  if (!ticket) {
    return {};
  }

  return {
    category: ticket.category,
    intent: ticket.intent,
    confidence: ticket.classification_confidence,
    reason: ticket.classification_reason,
    requires_human: ticket.requires_human,
  };
}

init();
