/* Shared helpers: CSRF-safe fetch, toasts, formatting */
const CSRF = document.querySelector('meta[name="csrf-token"]').content;

async function api(url, body) {
  const options = body === undefined
    ? { headers: { Accept: "application/json" } }
    : {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": CSRF, Accept: "application/json" },
        body: JSON.stringify(body),
      };
  let response;
  try {
    response = await fetch(url, options);
  } catch (err) {
    throw new Error("Cannot reach the server. Check your internet and try again.");
  }
  let data = {};
  try { data = await response.json(); } catch (err) { /* not JSON */ }
  if (response.status === 401) {
    window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname);
    throw new Error("Please log in first.");
  }
  if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");
  return data;
}

function toast(message, type) {
  const area = document.getElementById("toast-area");
  const el = document.createElement("div");
  el.className = "toast" + (type === "error" ? " error" : "");
  el.textContent = message;
  area.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function rupee(n) {
  n = Number(n) || 0;
  const whole = Number.isInteger(n);
  return "₹" + n.toLocaleString("en-IN", { minimumFractionDigits: whole ? 0 : 2, maximumFractionDigits: 2 });
}

function esc(text) {
  const d = document.createElement("div");
  d.textContent = text == null ? "" : String(text);
  return d.innerHTML;
}

const PLACEHOLDER = "/static/images/placeholder.svg";
function imgFallback(img) { img.onerror = null; img.src = PLACEHOLDER; }

// Auto-hide flash messages after a few seconds
document.querySelectorAll(".flash-wrap .flash-success, .flash-wrap .flash-info").forEach((el) => {
  setTimeout(() => { el.style.transition = "opacity .4s"; el.style.opacity = 0; setTimeout(() => el.remove(), 400); }, 4000);
});
