import {
  Activity,
  AlertCircle,
  Bot,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Clock3,
  LayoutDashboard,
  LockKeyhole,
  LogIn,
  LogOut,
  MessageSquareText,
  RefreshCw,
  RotateCcw,
  Send,
  ShieldCheck,
  Ticket,
  Users,
  X,
} from "lucide-react";
import { Fragment, useEffect, useMemo, useState } from "react";

const STORAGE_KEYS = {
  token: "yuv_support_token",
  user: "yuv_support_user",
};

const ROLE_OPTIONS = [
  { value: "admin", label: "Admin" },
  { value: "customer_success", label: "Customer Success" },
];

const NAV_ITEMS = [
  { id: "overview", label: "Visao Geral", icon: LayoutDashboard },
  { id: "tickets", label: "Tickets", icon: Ticket },
  { id: "ticket_messages", label: "Tickets Messages", icon: MessageSquareText },
  { id: "customers", label: "Customers", icon: Users },
  { id: "chat", label: "Chat Simulado", icon: Bot },
];

const TICKET_STATUSES = ["open", "in_progress", "pending", "resolved", "closed"];
const MESSAGE_SENDER_TYPES = ["customer", "user", "ai_agent", "system"];
const CHAT_QUICK_PROMPTS = [
  "Consultar ticket",
  "Problema de acesso",
  "Falar com humano",
];
const PAGE_SIZE = 100;

export function App() {
  const [activePage, setActivePage] = useState("overview");
  const [session, setSession] = useState(readSession);
  const [apiStatus, setApiStatus] = useState("checking");
  const [apiCheckedAt, setApiCheckedAt] = useState(null);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [notice, setNotice] = useState(null);
  const [ticketsState, setTicketsState] = useState({
    data: [],
    error: "",
    isLoading: false,
    loadedAt: null,
  });
  const [ticketMessagesState, setTicketMessagesState] = useState({
    data: [],
    error: "",
    isLoading: false,
    loadedAt: null,
  });
  const [messagesState, setMessagesState] = useState({
    data: [],
    error: "",
    isLoading: false,
    loadedAt: null,
    senderType: "",
  });
  const [customersState, setCustomersState] = useState({
    data: [],
    error: "",
    isLoading: false,
    loadedAt: null,
    openTickets: [],
  });
  const [expandedTicketIds, setExpandedTicketIds] = useState(() => new Set());

  const sessionLabel = useMemo(() => {
    if (!session?.user) {
      return "Login";
    }

    return roleLabel(session.user.role);
  }, [session]);

  const ticketsMetrics = useMemo(() => buildTicketsMetrics(ticketsState.data), [ticketsState.data]);
  const ticketMessagesByTicket = useMemo(
    () => groupMessagesByTicket(ticketMessagesState.data),
    [ticketMessagesState.data],
  );
  const activeNavItem = NAV_ITEMS.find((item) => item.id === activePage) || NAV_ITEMS[0];

  useEffect(() => {
    checkApi({ silent: true });
  }, []);

  useEffect(() => {
    if (activePage === "tickets" && session?.token && !ticketsState.loadedAt && !ticketsState.isLoading) {
      loadTickets();
    }
  }, [activePage, session?.token]);

  useEffect(() => {
    if (
      activePage === "ticket_messages" &&
      session?.token &&
      !messagesState.loadedAt &&
      !messagesState.isLoading
    ) {
      loadTicketMessages();
    }
  }, [activePage, session?.token]);

  useEffect(() => {
    if (activePage === "customers" && session?.token && !customersState.loadedAt && !customersState.isLoading) {
      loadCustomers();
    }
  }, [activePage, session?.token]);

  async function apiRequest(path, options = {}) {
    const headers = {
      Accept: "application/json",
      ...(options.headers || {}),
    };

    if (session?.token) {
      headers.Authorization = `Bearer ${session.token}`;
    }

    if (options.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`/api${path}`, {
      ...options,
      headers,
    });
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(typeof data?.detail === "string" ? data.detail : "Erro na API.");
    }

    return data;
  }

  async function checkApi({ silent = false } = {}) {
    setApiStatus("checking");

    try {
      const response = await fetch("/api/health");

      if (!response.ok) {
        throw new Error("API indisponivel.");
      }

      setApiStatus("online");
      setApiCheckedAt(new Date());

      if (!silent) {
        showNotice("API online.", "success");
      }
    } catch (error) {
      setApiStatus("offline");
      setApiCheckedAt(new Date());

      if (!silent) {
        showNotice(error.message, "error");
      }
    }
  }

  async function loadTickets() {
    if (!session?.token) {
      setIsLoginOpen(true);
      showNotice("Faca login para carregar tickets.", "error");
      return;
    }

    setTicketsState((current) => ({
      ...current,
      error: "",
      isLoading: true,
    }));
    setTicketMessagesState((current) => ({
      ...current,
      error: "",
      isLoading: true,
    }));

    try {
      const [ticketGroups, messages] = await Promise.all([
        Promise.all(TICKET_STATUSES.map((status) => loadTicketsByStatus(status))),
        fetchTicketMessages(""),
      ]);
      const tickets = dedupeTickets(ticketGroups.flat()).sort(sortTicketsByRecentActivity);

      setTicketsState({
        data: tickets,
        error: "",
        isLoading: false,
        loadedAt: new Date(),
      });
      setTicketMessagesState({
        data: messages,
        error: "",
        isLoading: false,
        loadedAt: new Date(),
      });
    } catch (error) {
      setTicketsState((current) => ({
        ...current,
        error: error.message,
        isLoading: false,
      }));
      setTicketMessagesState((current) => ({
        ...current,
        error: error.message,
        isLoading: false,
      }));
      showNotice(error.message, "error");
    }
  }

  async function loadTicketsByStatus(status) {
    const tickets = [];
    let offset = 0;

    while (true) {
      const params = new URLSearchParams({
        status,
        limit: String(PAGE_SIZE),
        offset: String(offset),
      });
      const page = await apiRequest(`/tickets?${params.toString()}`);
      const items = Array.isArray(page) ? page : [];

      tickets.push(...items);

      if (items.length < PAGE_SIZE) {
        break;
      }

      offset += PAGE_SIZE;
    }

    return tickets;
  }

  async function loadTicketMessages(senderType = messagesState.senderType) {
    if (!session?.token) {
      setIsLoginOpen(true);
      showNotice("Faca login para carregar mensagens.", "error");
      return;
    }

    setMessagesState((current) => ({
      ...current,
      error: "",
      isLoading: true,
      senderType,
    }));

    try {
      const messages = await fetchTicketMessages(senderType);

      setMessagesState({
        data: messages,
        error: "",
        isLoading: false,
        loadedAt: new Date(),
        senderType,
      });
    } catch (error) {
      setMessagesState((current) => ({
        ...current,
        error: error.message,
        isLoading: false,
      }));
      showNotice(error.message, "error");
    }
  }

  async function fetchTicketMessages(senderType = "") {
    const messages = [];
    let offset = 0;

    while (true) {
      const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(offset),
      });

      if (senderType) {
        params.set("sender_type", senderType);
      }

      const page = await apiRequest(`/tickets/messages?${params.toString()}`);
      const items = Array.isArray(page) ? page : [];

      messages.push(...items);

      if (items.length < PAGE_SIZE) {
        break;
      }

      offset += PAGE_SIZE;
    }

    return messages;
  }

  async function loadCustomers() {
    if (!session?.token) {
      setIsLoginOpen(true);
      showNotice("Faca login para carregar customers.", "error");
      return;
    }

    setCustomersState((current) => ({
      ...current,
      error: "",
      isLoading: true,
    }));

    try {
      const [customers, openTickets] = await Promise.all([
        fetchCustomers(),
        loadTicketsByStatus("open"),
      ]);

      setCustomersState({
        data: customers,
        error: "",
        isLoading: false,
        loadedAt: new Date(),
        openTickets,
      });
    } catch (error) {
      setCustomersState((current) => ({
        ...current,
        error: error.message,
        isLoading: false,
      }));
      showNotice(error.message, "error");
    }
  }

  async function fetchCustomers() {
    const customers = [];
    let offset = 0;

    while (true) {
      const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(offset),
      });
      const page = await apiRequest(`/customers?${params.toString()}`);
      const items = Array.isArray(page) ? page : [];

      customers.push(...items);

      if (items.length < PAGE_SIZE) {
        break;
      }

      offset += PAGE_SIZE;
    }

    return customers;
  }

  function saveSession(nextSession) {
    setSession(nextSession);
    localStorage.setItem(STORAGE_KEYS.token, nextSession.token);
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(nextSession.user));

    if (activePage === "tickets") {
      setTicketsState({
        data: [],
        error: "",
        isLoading: false,
        loadedAt: null,
      });
      setTicketMessagesState({
        data: [],
        error: "",
        isLoading: false,
        loadedAt: null,
      });
      setExpandedTicketIds(new Set());
    }

    if (activePage === "ticket_messages") {
      setMessagesState((current) => ({
        ...current,
        data: [],
        error: "",
        isLoading: false,
        loadedAt: null,
      }));
    }

    if (activePage === "customers") {
      setCustomersState({
        data: [],
        error: "",
        isLoading: false,
        loadedAt: null,
        openTickets: [],
      });
    }
  }

  function logout() {
    setSession(null);
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.user);
    setTicketsState({
      data: [],
      error: "",
      isLoading: false,
      loadedAt: null,
    });
    setTicketMessagesState({
      data: [],
      error: "",
      isLoading: false,
      loadedAt: null,
    });
    setMessagesState({
      data: [],
      error: "",
      isLoading: false,
      loadedAt: null,
      senderType: "",
    });
    setCustomersState({
      data: [],
      error: "",
      isLoading: false,
      loadedAt: null,
      openTickets: [],
    });
    setExpandedTicketIds(new Set());
    showNotice("Sessao encerrada.", "success");
  }

  function toggleTicketMessages(ticketId) {
    setExpandedTicketIds((current) => {
      const next = new Set(current);

      if (next.has(ticketId)) {
        next.delete(ticketId);
      } else {
        next.add(ticketId);
      }

      return next;
    });
  }

  function showNotice(message, type = "success") {
    setNotice({ message, type });
    window.clearTimeout(showNotice.timeoutId);
    showNotice.timeoutId = window.setTimeout(() => setNotice(null), 3600);
  }

  return (
    <main className="app-shell">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">{activeNavItem.label}</p>
            <h1>YUV Support</h1>
          </div>

          <div className="header-actions">
            <button className="button button-secondary" type="button" onClick={() => checkApi()}>
              <Activity size={18} />
              Checar API
            </button>
            <button
              className={`button session-button ${session ? "is-authenticated" : ""}`}
              type="button"
              onClick={() => setIsLoginOpen(true)}
            >
              {session ? <ShieldCheck size={18} /> : <LogIn size={18} />}
              {sessionLabel}
            </button>
          </div>
        </header>

        {activePage === "overview" && (
          <OverviewPage
            apiCheckedAt={apiCheckedAt}
            apiStatus={apiStatus}
            session={session}
            ticketsMetrics={ticketsMetrics}
          />
        )}

        {activePage === "tickets" && (
          <TicketsPage
            expandedTicketIds={expandedTicketIds}
            onLoginClick={() => setIsLoginOpen(true)}
            onRefresh={loadTickets}
            onToggleTicketMessages={toggleTicketMessages}
            session={session}
            ticketMessagesByTicket={ticketMessagesByTicket}
            ticketsState={ticketsState}
          />
        )}

        {activePage === "ticket_messages" && (
          <TicketMessagesPage
            messagesState={messagesState}
            onLoginClick={() => setIsLoginOpen(true)}
            onRefresh={() => loadTicketMessages()}
            onSenderTypeChange={loadTicketMessages}
            session={session}
          />
        )}

        {activePage === "customers" && (
          <CustomersPage
            customersState={customersState}
            onLoginClick={() => setIsLoginOpen(true)}
            onRefresh={loadCustomers}
            session={session}
          />
        )}

        {activePage === "chat" && <ChatSimulatorPage />}
      </section>

      {isLoginOpen && (
        <LoginModal
          session={session}
          onClose={() => setIsLoginOpen(false)}
          onLogin={saveSession}
          onLogout={logout}
          onNotice={showNotice}
        />
      )}

      {notice && <div className={`toast toast-${notice.type}`}>{notice.message}</div>}
    </main>
  );
}

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar" aria-label="Navegacao principal">
      <div className="brand">
        <span className="brand-mark">Y</span>
        <span>
          <strong>YUV Support</strong>
          <small>Data console</small>
        </span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;

          return (
            <button
              className={activePage === item.id ? "is-active" : ""}
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}

function OverviewPage({ apiCheckedAt, apiStatus, session, ticketsMetrics }) {
  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy">
          <span className={`status-dot status-${apiStatus}`}></span>
          <h2>Central de operacao</h2>
          <p>Ambiente local conectado ao fluxo de suporte.</p>
        </div>

        <div className="signal-grid" aria-label="Resumo do ambiente">
          <article>
            <Activity size={20} />
            <span>API</span>
            <strong>{apiStatusLabel(apiStatus)}</strong>
          </article>
          <article>
            <ShieldCheck size={20} />
            <span>Sessao</span>
            <strong>{session?.user ? session.user.name : "Sem login"}</strong>
          </article>
          <article>
            <Clock3 size={20} />
            <span>Ultima checagem</span>
            <strong>{formatDateTime(apiCheckedAt)}</strong>
          </article>
        </div>
      </section>

      <section className="dashboard-grid">
        <MetricCard label="Tickets carregados" value={ticketsMetrics.total || "--"} detail="View geral de tickets." />
        <MetricCard label="Handoff humano" value={ticketsMetrics.handoff || "--"} detail="Tickets que pedem atendimento." />
        <MetricCard
          label="Perfil atual"
          value={session?.user ? roleLabel(session.user.role) : "--"}
          detail={session?.user?.email || "Sem usuario autenticado."}
        />
      </section>
    </>
  );
}

function TicketsPage({
  expandedTicketIds,
  onLoginClick,
  onRefresh,
  onToggleTicketMessages,
  session,
  ticketMessagesByTicket,
  ticketsState,
}) {
  const metrics = useMemo(() => buildTicketsMetrics(ticketsState.data), [ticketsState.data]);

  if (!session?.token) {
    return (
      <section className="locked-panel">
        <span>
          <LockKeyhole size={24} />
        </span>
        <h2>Login necessario</h2>
        <p>Entre como Admin ou Customer Success para visualizar a tabela de tickets.</p>
        <button className="button" type="button" onClick={onLoginClick}>
          <LogIn size={18} />
          Fazer login
        </button>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Banco de dados</p>
          <h2>Tickets</h2>
        </div>
        <button className="button button-secondary" disabled={ticketsState.isLoading} type="button" onClick={onRefresh}>
          <RefreshCw size={18} />
          {ticketsState.isLoading ? "Atualizando" : "Atualizar"}
        </button>
      </div>

      <section className="dashboard-grid">
        <MetricCard label="Total" value={metrics.total} detail="Todos os status carregados." />
        <MetricCard label="Abertos" value={metrics.open} detail="Status open." />
        <MetricCard label="Handoff" value={metrics.handoff} detail="requires_human = true." />
      </section>

      {ticketsState.error && (
        <div className="inline-alert">
          <AlertCircle size={18} />
          {ticketsState.error}
        </div>
      )}

      <section className="data-panel">
        <div className="data-panel-header">
          <div>
            <strong>{ticketsState.data.length} tickets</strong>
            <span>Atualizado em {formatDateTime(ticketsState.loadedAt)}</span>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Ticket</th>
                <th>Status</th>
                <th>Prioridade</th>
                <th>Categoria</th>
                <th>Origem</th>
                <th>Customer</th>
                <th>Responsavel</th>
                <th>Handoff</th>
                <th>Ultima atividade</th>
              </tr>
            </thead>
            <tbody>
              {ticketsState.isLoading && (
                <tr>
                  <td className="empty-cell" colSpan="9">
                    Carregando tickets...
                  </td>
                </tr>
              )}

              {!ticketsState.isLoading && ticketsState.data.length === 0 && (
                <tr>
                  <td className="empty-cell" colSpan="9">
                    Nenhum ticket encontrado.
                  </td>
                </tr>
              )}

              {!ticketsState.isLoading &&
                ticketsState.data.map((ticket) => {
                  const messages = ticketMessagesByTicket.get(ticket.id) || [];
                  const isExpanded = expandedTicketIds.has(ticket.id);

                  return (
                    <Fragment key={ticket.id}>
                      <tr>
                        <td className="ticket-title-cell">
                          <button
                            className="expand-button"
                            disabled={!messages.length}
                            type="button"
                            onClick={() => onToggleTicketMessages(ticket.id)}
                            aria-label={isExpanded ? "Fechar mensagens" : "Abrir mensagens"}
                          >
                            {isExpanded ? <ChevronDown size={17} /> : <ChevronRight size={17} />}
                          </button>
                          <div>
                            <div className="ticket-title-line">
                              <strong>{ticket.title || "Sem titulo"}</strong>
                              <span className="message-count">{messages.length} mensagens</span>
                            </div>
                            <span>{shortId(ticket.id)}</span>
                          </div>
                        </td>
                        <td>
                          <StatusBadge value={ticket.status} />
                        </td>
                        <td>{ticket.priority || "--"}</td>
                        <td>{ticket.category || "--"}</td>
                        <td>
                          <strong>{ticket.source || "--"}</strong>
                          <span>{ticket.channel || "--"}</span>
                        </td>
                        <td>{shortId(ticket.customer_id)}</td>
                        <td>{shortId(ticket.assigned_user_id)}</td>
                        <td>{ticket.requires_human ? "Sim" : "Nao"}</td>
                        <td>{formatDateTime(ticket.last_message_at || ticket.updated_at || ticket.created_at)}</td>
                      </tr>
                      {isExpanded && (
                      <tr className="expanded-row">
                          <td colSpan="9">
                            <div className="ticket-messages-panel">
                              {messages.map((message) => (
                                <article className="ticket-message-item" key={message.id}>
                                  <div className="ticket-message-meta">
                                    <MessageSenderBadge value={message.sender_type} />
                                    <time>{formatDateTime(message.created_at)}</time>
                                  </div>
                                  <p>{message.body}</p>
                                </article>
                              ))}
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

function TicketMessagesPage({
  messagesState,
  onLoginClick,
  onRefresh,
  onSenderTypeChange,
  session,
}) {
  const insights = useMemo(() => buildMessageInsights(messagesState.data), [messagesState.data]);
  const metrics = useMemo(() => buildMessagesMetrics(insights), [insights]);
  const categoryRanking = useMemo(
    () => rankBy(insights, (insight) => insight.category),
    [insights],
  );
  const intentRanking = useMemo(
    () => rankBy(insights, (insight) => insight.intent),
    [insights],
  );
  const termsRanking = useMemo(
    () => rankTerms(insights),
    [insights],
  );

  if (!session?.token) {
    return (
      <section className="locked-panel">
        <span>
          <LockKeyhole size={24} />
        </span>
        <h2>Login necessario</h2>
        <p>Entre como Admin ou Customer Success para visualizar as mensagens dos tickets.</p>
        <button className="button" type="button" onClick={onLoginClick}>
          <LogIn size={18} />
          Fazer login
        </button>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Inteligencia comercial</p>
          <h2>Temas das mensagens</h2>
        </div>

        <div className="toolbar">
          <label className="compact-field">
            Remetente
            <select
              disabled={messagesState.isLoading}
              onChange={(event) => onSenderTypeChange(event.target.value)}
              value={messagesState.senderType}
            >
              <option value="">Todos</option>
              {MESSAGE_SENDER_TYPES.map((senderType) => (
                <option key={senderType} value={senderType}>
                  {senderType}
                </option>
              ))}
            </select>
          </label>
          <button className="button button-secondary" disabled={messagesState.isLoading} type="button" onClick={onRefresh}>
            <RefreshCw size={18} />
            {messagesState.isLoading ? "Atualizando" : "Atualizar"}
          </button>
        </div>
      </div>

      <section className="dashboard-grid">
        <MetricCard label="Classificacoes" value={metrics.classified} detail="Mensagens com assunto identificado." />
        <MetricCard label="Categorias" value={metrics.categories} detail="Temas distintos encontrados." />
        <MetricCard label="Confianca media" value={metrics.averageConfidence} detail="Score medio do classificador." />
      </section>

      <section className="insight-grid">
        <RankingPanel title="Categorias mais frequentes" items={categoryRanking} total={insights.length} />
        <RankingPanel title="Intencoes mais frequentes" items={intentRanking} total={insights.length} />
        <RankingPanel title="Termos mais citados" items={termsRanking} total={termsRanking[0]?.count || 0} />
      </section>

      {messagesState.error && (
        <div className="inline-alert">
          <AlertCircle size={18} />
          {messagesState.error}
        </div>
      )}

      <section className="data-panel">
        <div className="data-panel-header">
          <div>
            <strong>{insights.length} sinais classificados</strong>
            <span>{messagesState.data.length} mensagens analisadas - atualizado em {formatDateTime(messagesState.loadedAt)}</span>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Categoria</th>
                <th>Intencao / assunto</th>
                <th>Confianca</th>
                <th>Termos</th>
                <th>Ticket</th>
                <th>Mensagem relacionada</th>
                <th>Justificativa</th>
                <th>Origem</th>
                <th>Criada em</th>
              </tr>
            </thead>
            <tbody>
              {messagesState.isLoading && (
                <tr>
                  <td className="empty-cell" colSpan="9">
                    Carregando mensagens...
                  </td>
                </tr>
              )}

              {!messagesState.isLoading && insights.length === 0 && (
                <tr>
                  <td className="empty-cell" colSpan="9">
                    Nenhuma classificacao encontrada nas mensagens carregadas.
                  </td>
                </tr>
              )}

              {!messagesState.isLoading &&
                insights.map((insight) => (
                  <tr key={insight.messageId}>
                    <td>
                      <strong>{insight.category}</strong>
                    </td>
                    <td>{formatIntent(insight.intent)}</td>
                    <td>{formatConfidence(insight.confidence)}</td>
                    <td className="terms-cell">{insight.searchTerms.length ? insight.searchTerms.join(", ") : "--"}</td>
                    <td>
                      <strong>{insight.ticketTitle || "Sem titulo"}</strong>
                      <span>{shortId(insight.ticketId)}</span>
                    </td>
                    <td className="message-body">{insight.relatedMessage || "--"}</td>
                    <td className="message-body">{insight.reason || "--"}</td>
                    <td>
                      <MessageSenderBadge value={insight.senderType} />
                      <span>{insight.source === "classifier" ? "classifier" : "ticket"}</span>
                    </td>
                    <td>{formatDateTime(insight.createdAt)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

function CustomersPage({ customersState, onLoginClick, onRefresh, session }) {
  const [searchTerm, setSearchTerm] = useState("");
  const metrics = useMemo(
    () => buildCustomersMetrics(customersState.data, customersState.openTickets),
    [customersState.data, customersState.openTickets],
  );
  const openTicketCountsByCustomer = useMemo(
    () => countTicketsByCustomer(customersState.openTickets),
    [customersState.openTickets],
  );
  const filteredCustomers = useMemo(
    () => filterCustomers(customersState.data, { query: searchTerm }),
    [customersState.data, searchTerm],
  );
  const domainRanking = useMemo(
    () => rankCustomerDomains(customersState.data),
    [customersState.data],
  );
  const fieldRanking = useMemo(
    () => rankCustomerFields(customersState.data),
    [customersState.data],
  );

  if (!session?.token) {
    return (
      <section className="locked-panel">
        <span>
          <LockKeyhole size={24} />
        </span>
        <h2>Login necessario</h2>
        <p>Entre como Admin ou Customer Success para visualizar os customers.</p>
        <button className="button" type="button" onClick={onLoginClick}>
          <LogIn size={18} />
          Fazer login
        </button>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Banco de dados</p>
          <h2>Customers</h2>
        </div>

        <div className="toolbar">
          <label className="compact-field search-field">
            Buscar
            <input
              disabled={customersState.isLoading}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Nome, email, telefone..."
              type="search"
              value={searchTerm}
            />
          </label>
          <button className="button button-secondary" disabled={customersState.isLoading} type="button" onClick={onRefresh}>
            <RefreshCw size={18} />
            {customersState.isLoading ? "Atualizando" : "Atualizar"}
          </button>
        </div>
      </div>

      <section className="dashboard-grid dashboard-grid-compact">
        <MetricCard label="Total" value={metrics.total} detail="Customers carregados." />
        <MetricCard label="Clientes em aberto" value={metrics.openCustomers} detail={`${metrics.openTickets} tickets abertos.`} />
      </section>

      <section className="insight-grid insight-grid-compact">
        <RankingPanel
          emptyLabel="Sem emails registrados."
          title="Dominios de email"
          items={domainRanking}
          total={customersState.data.length}
        />
        <RankingPanel
          emptyLabel="Sem dados preenchidos."
          title="Dados preenchidos"
          items={fieldRanking}
          total={customersState.data.length}
        />
      </section>

      {customersState.error && (
        <div className="inline-alert">
          <AlertCircle size={18} />
          {customersState.error}
        </div>
      )}

      <section className="data-panel">
        <div className="data-panel-header">
          <div>
            <strong>{filteredCustomers.length} customers</strong>
            <span>{customersState.data.length} carregados - atualizado em {formatDateTime(customersState.loadedAt)}</span>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Contato</th>
                <th>Documento</th>
                <th>Tickets abertos</th>
                <th>Criado em</th>
                <th>Atualizado em</th>
              </tr>
            </thead>
            <tbody>
              {customersState.isLoading && (
                <tr>
                  <td className="empty-cell" colSpan="6">
                    Carregando customers...
                  </td>
                </tr>
              )}

              {!customersState.isLoading && filteredCustomers.length === 0 && (
                <tr>
                  <td className="empty-cell" colSpan="6">
                    Nenhum customer encontrado.
                  </td>
                </tr>
              )}

              {!customersState.isLoading &&
                filteredCustomers.map((customer) => (
                  <tr key={customer.id}>
                    <td className="customer-name-cell">
                      <strong>{customer.name || "Sem nome"}</strong>
                      <span>{shortId(customer.id)}</span>
                    </td>
                    <td className="contact-stack">
                      <strong>{customer.email || "--"}</strong>
                      <span>{customer.phone || "--"}</span>
                    </td>
                    <td>{customer.document || "--"}</td>
                    <td>{openTicketCountsByCustomer.get(customer.id) || 0}</td>
                    <td>{formatDateTime(customer.created_at)}</td>
                    <td>{formatDateTime(customer.updated_at)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

function ChatSimulatorPage() {
  const [messages, setMessages] = useState(createInitialChatMessages);
  const [draft, setDraft] = useState("");

  function sendMessage(value = draft) {
    const text = safeText(value);

    if (!text) {
      return;
    }

    const userMessage = {
      id: createChatId("user"),
      role: "user",
      text,
      createdAt: new Date(),
    };
    const assistantMessage = {
      id: createChatId("assistant"),
      role: "assistant",
      text: buildSimulatedChatReply(text),
      createdAt: new Date(),
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setDraft("");
  }

  function submitMessage(event) {
    event.preventDefault();
    sendMessage();
  }

  function resetChat() {
    setMessages(createInitialChatMessages());
    setDraft("");
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Simulacao</p>
          <h2>Chat</h2>
        </div>

        <button className="button button-ghost" type="button" onClick={resetChat}>
          <RotateCcw size={18} />
          Limpar
        </button>
      </div>

      <section className="chat-panel">
        <div className="chat-thread" aria-live="polite">
          {messages.map((message) => (
            <article className={`chat-message chat-message-${message.role}`} key={message.id}>
              <span>{message.role === "user" ? "Cliente" : "Assistente"}</span>
              <p>{message.text}</p>
              <time>{formatChatTime(message.createdAt)}</time>
            </article>
          ))}
        </div>

        <div className="chat-quick-actions">
          {CHAT_QUICK_PROMPTS.map((prompt) => (
            <button key={prompt} type="button" onClick={() => sendMessage(prompt)}>
              {prompt}
            </button>
          ))}
        </div>

        <form className="chat-composer" onSubmit={submitMessage}>
          <input
            aria-label="Mensagem"
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Mensagem"
            type="text"
            value={draft}
          />
          <button className="button" type="submit">
            <Send size={18} />
            Enviar
          </button>
        </form>
      </section>
    </section>
  );
}

function PlaceholderPage({ description, icon: Icon, title }) {
  return (
    <section className="placeholder-panel">
      <span>
        <Icon size={26} />
      </span>
      <h2>{title}</h2>
      <p>{description}</p>
    </section>
  );
}

function MetricCard({ detail, label, value }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function RankingPanel({ emptyLabel = "Sem dados classificados.", items, title, total }) {
  return (
    <article className="ranking-panel">
      <h3>{title}</h3>
      <div className="ranking-list">
        {items.length === 0 && <p className="empty-ranking">{emptyLabel}</p>}
        {items.map((item) => (
          <div className="ranking-row" key={item.label}>
            <div className="ranking-row-main">
              <span>{item.label}</span>
              <div className="ranking-bar">
                <span style={{ width: `${rankingPercent(item.count, total)}%` }}></span>
              </div>
            </div>
            <strong>{item.count}</strong>
          </div>
        ))}
      </div>
    </article>
  );
}

function StatusBadge({ value }) {
  return <span className={`status-badge status-badge-${value || "unknown"}`}>{value || "--"}</span>;
}

function MessageSenderBadge({ value }) {
  return <span className={`sender-badge sender-badge-${value || "unknown"}`}>{value || "--"}</span>;
}

function LoginModal({ session, onClose, onLogin, onLogout, onNotice }) {
  const [selectedRole, setSelectedRole] = useState("admin");
  const [email, setEmail] = useState(session?.user?.email || "");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function submitLogin(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(typeof data?.detail === "string" ? data.detail : "Login recusado.");
      }

      if (data?.user?.role !== selectedRole) {
        throw new Error(`Este usuario nao possui permissao de ${roleLabel(selectedRole)}.`);
      }

      onLogin({
        token: data.access_token,
        user: data.user,
      });
      onNotice(`Entrou como ${roleLabel(selectedRole)}.`, "success");
      onClose();
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleLogout() {
    onLogout();
    onClose();
  }

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <section
        className="login-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="login-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button className="icon-button" type="button" aria-label="Fechar" onClick={onClose}>
          <X size={18} />
        </button>

        <div className="modal-heading">
          <span className="modal-icon">
            <LockKeyhole size={22} />
          </span>
          <div>
            <p className="eyebrow">Login</p>
            <h2 id="login-title">Entrar na plataforma</h2>
          </div>
        </div>

        {session?.user && (
          <div className="current-session">
            <CheckCircle2 size={18} />
            <div>
              <strong>{session.user.name}</strong>
              <span>
                {roleLabel(session.user.role)} - {session.user.email}
              </span>
            </div>
            <button className="button button-ghost" type="button" onClick={handleLogout}>
              <LogOut size={17} />
              Sair
            </button>
          </div>
        )}

        <form className="login-form" onSubmit={submitLogin}>
          <fieldset>
            <legend>Perfil solicitado</legend>
            <div className="role-switch">
              {ROLE_OPTIONS.map((option) => (
                <button
                  className={selectedRole === option.value ? "is-selected" : ""}
                  key={option.value}
                  type="button"
                  onClick={() => setSelectedRole(option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </fieldset>

          <label>
            Email
            <input
              autoComplete="username"
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              value={email}
            />
          </label>

          <label>
            Senha
            <input
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              value={password}
            />
          </label>

          {error && <p className="form-error">{error}</p>}

          <button className="button button-full" disabled={isSubmitting} type="submit">
            <LogIn size={18} />
            {isSubmitting ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </section>
    </div>
  );
}

function buildTicketsMetrics(tickets) {
  return {
    total: tickets.length,
    open: tickets.filter((ticket) => ticket.status === "open").length,
    handoff: tickets.filter((ticket) => ticket.requires_human).length,
  };
}

function buildMessagesMetrics(insights) {
  const confidences = insights
    .map((insight) => insight.confidence)
    .filter((confidence) => typeof confidence === "number" && !Number.isNaN(confidence));
  const averageConfidence = confidences.length
    ? confidences.reduce((total, confidence) => total + confidence, 0) / confidences.length
    : null;

  return {
    classified: insights.length,
    categories: new Set(insights.map((insight) => insight.category).filter(Boolean)).size,
    averageConfidence: formatConfidence(averageConfidence),
  };
}

function buildCustomersMetrics(customers, openTickets = []) {
  const customerIds = new Set(customers.map((customer) => customer.id).filter(Boolean));
  const openCustomerIds = new Set(
    openTickets
      .map((ticket) => ticket.customer_id)
      .filter((customerId) => customerId && customerIds.has(customerId)),
  );

  return {
    total: customers.length,
    openCustomers: openCustomerIds.size,
    openTickets: openTickets.length,
  };
}

function countTicketsByCustomer(tickets = []) {
  const counts = new Map();

  tickets.forEach((ticket) => {
    if (!ticket.customer_id) {
      return;
    }

    counts.set(ticket.customer_id, (counts.get(ticket.customer_id) || 0) + 1);
  });

  return counts;
}

function filterCustomers(customers, { query }) {
  const normalizedQuery = safeText(query).toLowerCase();

  return customers.filter((customer) => {
    const searchable = [
      customer.name,
      customer.email,
      customer.phone,
      customer.document,
      customer.id,
    ]
      .map((value) => safeText(value).toLowerCase())
      .join(" ");
    const matchesQuery = !normalizedQuery || searchable.includes(normalizedQuery);

    return matchesQuery;
  });
}

function rankCustomerDomains(customers) {
  const counts = new Map();

  customers.forEach((customer) => {
    const domain = safeText(customer.email).split("@").at(1);

    if (!domain) {
      return;
    }

    counts.set(domain, (counts.get(domain) || 0) + 1);
  });

  return [...counts.entries()]
    .map(([label, count]) => ({ label, count }))
    .sort((first, second) => second.count - first.count || first.label.localeCompare(second.label))
    .slice(0, 6);
}

function rankCustomerFields(customers) {
  const fields = [
    ["Email", (customer) => customer.email],
    ["Telefone", (customer) => customer.phone],
    ["Documento", (customer) => customer.document],
  ];

  return fields
    .map(([label, getValue]) => ({
      label,
      count: customers.filter((customer) => Boolean(getValue(customer))).length,
    }))
    .filter((item) => item.count > 0)
    .sort((first, second) => second.count - first.count || first.label.localeCompare(second.label));
}

function createInitialChatMessages() {
  return [
    {
      id: createChatId("assistant"),
      role: "assistant",
      text: "Ola. Sou o assistente simulado da YUV. Posso consultar ticket, registrar problema ou encaminhar para atendimento.",
      createdAt: new Date(),
    },
  ];
}

function buildSimulatedChatReply(message) {
  const text = safeText(message).toLowerCase();

  if (text.includes("humano") || text.includes("atendente") || text.includes("pessoa")) {
    return "Certo. Eu encaminharia para Customer Success e manteria o ticket aberto para acompanhamento.";
  }

  if (text.includes("ticket") || text.includes("protocolo") || text.includes("status")) {
    return "Perfeito. Eu pediria o numero do ticket e retornaria status, ultima atualizacao e responsavel.";
  }

  if (text.includes("acesso") || text.includes("login") || text.includes("senha")) {
    return "Entendi. Eu registraria como problema de acesso, pediria o email afetado e marcaria prioridade.";
  }

  if (
    text.includes("erro") ||
    text.includes("problema") ||
    text.includes("bug") ||
    text.includes("lento") ||
    text.includes("instabilidade")
  ) {
    return "Recebido. Eu abriria um ticket tecnico com resumo do problema e pediria impacto e horario de ocorrencia.";
  }

  return "Recebido. Eu criaria um ticket com essa mensagem e classificaria para o time analisar.";
}

function createChatId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function formatChatTime(value) {
  if (!value) {
    return "--";
  }

  const date = value instanceof Date ? value : new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "--";
  }

  return new Intl.DateTimeFormat("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function buildMessageInsights(messages) {
  const messagesByTicket = groupMessagesByTicket(messages);
  const ticketsWithClassifier = new Set(
    messages
      .filter((message) => hasExplicitClassification(message))
      .map((message) => message.ticket_id),
  );

  return messages
    .map((message) => {
      const allowTicketFallback =
        message.sender_type === "customer" && !ticketsWithClassifier.has(message.ticket_id);
      const classification = normalizeMessageClassification(message, { allowTicketFallback });

      if (!classification) {
        return null;
      }

      const relatedCustomerMessage = findPreviousCustomerMessage(
        message,
        messagesByTicket.get(message.ticket_id) || [],
      );

      return {
        ...classification,
        createdAt: message.created_at,
        messageId: message.id,
        relatedMessage: relatedCustomerMessage?.body || message.body,
        senderType: message.sender_type,
        ticketId: message.ticket_id,
        ticketTitle: message.ticket?.title,
      };
    })
    .filter(Boolean)
    .sort((first, second) => new Date(second.createdAt) - new Date(first.createdAt));
}

function normalizeMessageClassification(message, { allowTicketFallback }) {
  const explicitClassification = message.metadata?.classification;
  const hasExplicit = isNonEmptyObject(explicitClassification);
  const ticket = message.ticket || {};

  if (!hasExplicit && !allowTicketFallback) {
    return null;
  }

  const classification = hasExplicit ? explicitClassification : {};
  const category = safeText(
    classification.categoria ||
    classification.category ||
    ticket.category ||
    "",
  );
  const intent = safeText(
    classification.intencao ||
    classification.intent ||
    ticket.intent ||
    "nao_identificada",
  );
  const confidence = normalizeConfidence(
    classification.confianca ??
    classification.confidence ??
    ticket.classification_confidence,
  );
  const reason = safeText(
    classification.justificativa ||
    classification.reason ||
    ticket.classification_reason ||
    "",
  );
  const searchTerms = normalizeSearchTerms(
    classification.termos_busca ||
    classification.search_terms ||
    classification.terms,
  );

  if (!category && !intent && !reason && !searchTerms.length) {
    return null;
  }

  return {
    category: category || "outros",
    confidence,
    intent: intent || "nao_identificada",
    reason,
    searchTerms,
    source: hasExplicit ? "classifier" : "ticket",
  };
}

function hasExplicitClassification(message) {
  return isNonEmptyObject(message.metadata?.classification);
}

function isNonEmptyObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value) && Object.keys(value).length);
}

function groupMessagesByTicket(messages) {
  const grouped = new Map();

  messages.forEach((message) => {
    const currentMessages = grouped.get(message.ticket_id) || [];
    currentMessages.push(message);
    grouped.set(message.ticket_id, currentMessages);
  });

  grouped.forEach((ticketMessages) => {
    ticketMessages.sort((first, second) => new Date(first.created_at) - new Date(second.created_at));
  });

  return grouped;
}

function findPreviousCustomerMessage(message, ticketMessages) {
  const messageTime = new Date(message.created_at).getTime();

  return ticketMessages
    .filter((candidate) => candidate.sender_type === "customer")
    .filter((candidate) => new Date(candidate.created_at).getTime() <= messageTime)
    .at(-1);
}

function rankBy(items, getValue) {
  const counts = new Map();

  items.forEach((item) => {
    const value = String(getValue(item) || "").trim();

    if (!value || value === "--") {
      return;
    }

    counts.set(value, (counts.get(value) || 0) + 1);
  });

  return [...counts.entries()]
    .map(([label, count]) => ({ label: formatIntent(label), count }))
    .sort((first, second) => second.count - first.count || first.label.localeCompare(second.label))
    .slice(0, 6);
}

function rankTerms(insights) {
  const counts = new Map();

  insights.forEach((insight) => {
    insight.searchTerms.forEach((term) => {
      counts.set(term, (counts.get(term) || 0) + 1);
    });
  });

  return [...counts.entries()]
    .map(([label, count]) => ({ label, count }))
    .sort((first, second) => second.count - first.count || first.label.localeCompare(second.label))
    .slice(0, 6);
}

function rankingPercent(count, total) {
  if (!count || !total) {
    return 0;
  }

  return Math.max(8, Math.round((count / total) * 100));
}

function normalizeSearchTerms(value) {
  if (!value) {
    return [];
  }

  const terms = Array.isArray(value) ? value : String(value).split(",");

  return terms
    .map((term) => String(term).trim())
    .filter(Boolean)
    .slice(0, 6);
}

function normalizeConfidence(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const confidence = Number(value);

  if (Number.isNaN(confidence)) {
    return null;
  }

  return Math.min(1, Math.max(0, confidence));
}

function dedupeTickets(tickets) {
  return [...new Map(tickets.map((ticket) => [ticket.id, ticket])).values()];
}

function sortTicketsByRecentActivity(first, second) {
  return getTicketTime(second) - getTicketTime(first);
}

function getTicketTime(ticket) {
  return new Date(ticket.last_message_at || ticket.updated_at || ticket.created_at || 0).getTime();
}

function readSession() {
  const token = localStorage.getItem(STORAGE_KEYS.token);
  const user = readStoredJson(STORAGE_KEYS.user);

  if (!token || !user) {
    return null;
  }

  return { token, user };
}

function readStoredJson(key) {
  const value = localStorage.getItem(key);

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function roleLabel(role) {
  const labels = {
    admin: "Admin",
    customer_success: "Customer Success",
    agent: "Agent",
  };

  return labels[role] || role || "--";
}

function apiStatusLabel(status) {
  const labels = {
    checking: "Verificando",
    online: "Online",
    offline: "Offline",
  };

  return labels[status] || status;
}

function formatDateTime(value) {
  if (!value) {
    return "--";
  }

  const date = value instanceof Date ? value : new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "--";
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

function shortId(value) {
  if (!value) {
    return "--";
  }

  return String(value).slice(0, 8);
}

function safeText(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value).trim();
}

function formatConfidence(value) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "--";
  }

  return `${Math.round(value * 100)}%`;
}

function formatIntent(value) {
  if (!value) {
    return "--";
  }

  return String(value).replaceAll("_", " ");
}

function metadataSummary(metadata) {
  if (!metadata || typeof metadata !== "object") {
    return "--";
  }

  const keys = Object.keys(metadata);
  if (!keys.length) {
    return "--";
  }

  return keys.slice(0, 3).join(", ");
}
