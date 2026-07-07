import {
  Activity,
  CheckCircle2,
  Clock3,
  LockKeyhole,
  LogIn,
  LogOut,
  ShieldCheck,
  UserRoundCheck,
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

export function App() {
  const [session, setSession] = useState(readSession);
  const [apiStatus, setApiStatus] = useState("checking");
  const [apiCheckedAt, setApiCheckedAt] = useState(null);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [notice, setNotice] = useState(null);

  const sessionLabel = useMemo(() => {
    if (!session?.user) {
      return "Login";
    }

    return roleLabel(session.user.role);
  }, [session]);

  useEffect(() => {
    checkApi({ silent: true });
  }, []);

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

  function saveSession(nextSession) {
    setSession(nextSession);
    localStorage.setItem(STORAGE_KEYS.token, nextSession.token);
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(nextSession.user));
  }

  function logout() {
    setSession(null);
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.user);
    showNotice("Sessao encerrada.", "success");
  }

  function showNotice(message, type = "success") {
    setNotice({ message, type });
    window.clearTimeout(showNotice.timeoutId);
    showNotice.timeoutId = window.setTimeout(() => setNotice(null), 3600);
  }

  return (
    <main className="app">
      <section className="overview">
        <header className="overview-header">
          <div>
            <p className="eyebrow">Visao Geral</p>
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
              <UserRoundCheck size={20} />
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
          <article className="metric-card">
            <span>Tickets abertos</span>
            <strong>--</strong>
            <small>Sem dados carregados.</small>
          </article>
          <article className="metric-card">
            <span>Clientes ativos</span>
            <strong>--</strong>
            <small>Sem dados carregados.</small>
          </article>
          <article className="metric-card">
            <span>Perfil atual</span>
            <strong>{session?.user ? roleLabel(session.user.role) : "--"}</strong>
            <small>{session?.user?.email || "Sem usuario autenticado."}</small>
          </article>
        </section>
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

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(value);
}
