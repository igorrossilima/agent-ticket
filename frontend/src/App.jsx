import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock3,
  Database,
  LayoutDashboard,
  LockKeyhole,
  LogIn,
  LogOut,
  MessageSquareText,
  RefreshCw,
  ShieldCheck,
  Ticket,
  Users,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

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
];

const TICKET_STATUSES = ["open", "in_progress", "pending", "resolved", "closed"];
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

  const sessionLabel = useMemo(() => {
    if (!session?.user) {
      return "Login";
    }

    return roleLabel(session.user.role);
  }, [session]);

  const ticketsMetrics = useMemo(() => buildTicketsMetrics(ticketsState.data), [ticketsState.data]);
  const activeNavItem = NAV_ITEMS.find((item) => item.id === activePage) || NAV_ITEMS[0];

  useEffect(() => {
    checkApi({ silent: true });
  }, []);

  useEffect(() => {
    if (activePage === "tickets" && session?.token && !ticketsState.loadedAt && !ticketsState.isLoading) {
      loadTickets();
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

    try {
      const ticketGroups = await Promise.all(
        TICKET_STATUSES.map((status) => loadTicketsByStatus(status)),
      );
      const tickets = dedupeTickets(ticketGroups.flat()).sort(sortTicketsByRecentActivity);

      setTicketsState({
        data: tickets,
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
    showNotice("Sessao encerrada.", "success");
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
            onLoginClick={() => setIsLoginOpen(true)}
            onRefresh={loadTickets}
            session={session}
            ticketsState={ticketsState}
          />
        )}

        {activePage === "ticket_messages" && (
          <PlaceholderPage
            icon={MessageSquareText}
            title="Tickets Messages"
            description="Em breve."
          />
        )}

        {activePage === "customers" && (
          <PlaceholderPage
            icon={Users}
            title="Customers"
            description="Em breve."
          />
        )}
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

function TicketsPage({ onLoginClick, onRefresh, session, ticketsState }) {
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
                ticketsState.data.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>
                      <strong>{ticket.title || "Sem titulo"}</strong>
                      <span>{shortId(ticket.id)}</span>
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
                ))}
            </tbody>
          </table>
        </div>
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

function StatusBadge({ value }) {
  return <span className={`status-badge status-badge-${value || "unknown"}`}>{value || "--"}</span>;
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
