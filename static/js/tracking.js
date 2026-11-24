/* Order tracking: checks the status every 10 seconds */
(() => {
  const box = document.getElementById("tracker");
  if (!box) return;
  const id = box.dataset.orderId;
  let current = box.dataset.status;
  let timer = null;

  function paint(data) {
    box.querySelectorAll(".step").forEach((li) => {
      li.classList.toggle("done", data.reached.includes(li.dataset.step));
      li.classList.toggle("current", li.dataset.step === data.status);
    });
    document.getElementById("cancelled-note").hidden = data.status !== "cancelled";
    if (data.status === "delivered" || data.status === "cancelled") {
      clearInterval(timer);
      document.getElementById("live-note").textContent = data.status === "delivered" ? "Delivered. Enjoy your meal!" : "";
    }
  }

  async function check() {
    try {
      const data = await api(`/api/orders/${id}/status`);
      if (data.status !== current) { current = data.status; toast("Order update: " + data.label); }
      paint(data);
    } catch (err) { /* try again next time */ }
  }

  timer = setInterval(check, 10000);
  if (current === "delivered" || current === "cancelled") clearInterval(timer);
})();
