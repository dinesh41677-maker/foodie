/* Floating cart bar (every page) + cart page */
function updateCartBadges(cart) {
  const count = cart.bill.item_count;
  document.querySelectorAll("[data-cart-count]").forEach((b) => { b.textContent = count; b.hidden = count === 0; });
  const bar = document.getElementById("cart-bar");
  if (bar) {
    bar.hidden = count === 0;
    document.getElementById("cart-bar-count").textContent = count;
    document.getElementById("cart-bar-plural").textContent = count === 1 ? "" : "s";
    document.getElementById("cart-bar-total").textContent = rupee(cart.bill.grand_total);
  }
}

async function refreshCart() {
  try {
    const cart = await api("/api/cart");
    updateCartBadges(cart);
    renderCartPage(cart);
    return cart;
  } catch (err) { /* bar stays hidden if the cart cannot load */ }
}

/* ---------- cart page ---------- */
function renderCartPage(cart) {
  const box = document.getElementById("cart-content");
  if (!box) return;
  if (!cart.items.length) {
    box.innerHTML = `<div class="empty"><h3>Your cart is empty</h3>
      <p>Good food is waiting on the menu.</p><a class="btn" href="/">Browse the menu</a></div>`;
    return;
  }
  const b = cart.bill;
  const lines = cart.items.map((it) => `
    <div class="cart-line" data-id="${it.id}">
      <img src="${esc(it.image_url)}" alt="${esc(it.name)}" onerror="imgFallback(this)">
      <div>
        <div class="cart-name"><span class="diet ${it.food_type}"></span>${esc(it.name)}</div>
        ${it.addons.length ? `<ul class="cart-addons">${it.addons.map((a) => `<li>+ ${esc(a.name)} (${rupee(a.price)})</li>`).join("")}</ul>` : ""}
        <div class="cart-unit">${rupee(it.unit_price + it.addon_each)} each</div>
      </div>
      <div class="cart-right">
        <div class="qty">
          <button data-act="dec" aria-label="Decrease quantity">−</button>
          <span>${it.qty}</span>
          <button data-act="inc" aria-label="Increase quantity">+</button>
        </div>
        <strong>${rupee(it.line_total)}</strong>
        <button class="remove-btn" data-act="remove">Remove</button>
      </div>
    </div>`).join("");
  const toFree = b.free_delivery_above - (b.mrp_total - b.discount + b.addon_total);
  box.innerHTML = `
    <div class="panel">${lines}</div>
    <div class="panel">
      <h2>Bill details</h2>
      <dl class="bill">
        <div><dt>Item total</dt><dd>${rupee(b.mrp_total)}</dd></div>
        ${b.discount > 0 ? `<div class="green"><dt>Discount</dt><dd>− ${rupee(b.discount)}</dd></div>` : ""}
        ${b.addon_total > 0 ? `<div><dt>Add-ons</dt><dd>${rupee(b.addon_total)}</dd></div>` : ""}
        <div><dt>Delivery fee</dt><dd>${b.delivery_fee === 0 ? '<span class="green">FREE</span>' : rupee(b.delivery_fee)}</dd></div>
        <div><dt>Taxes (${b.tax_percent}% GST)</dt><dd>${rupee(b.tax)}</dd></div>
        <div class="grand"><dt>Grand total</dt><dd>${rupee(b.grand_total)}</dd></div>
      </dl>
      ${toFree > 0 ? `<div class="free-note">Add ${rupee(toFree)} more for free delivery</div>` : ""}
      <a class="btn btn-block" href="/checkout">Proceed to checkout</a>
      <p class="center"><a href="/">Add more items</a></p>
    </div>`;
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-act]");
  const line = btn && btn.closest(".cart-line");
  if (!btn || !line) return;
  const id = Number(line.dataset.id);
  const qty = Number(line.querySelector(".qty span").textContent);
  btn.disabled = true;
  try {
    let cart;
    if (btn.dataset.act === "remove") cart = await api("/api/cart/remove", { item_id: id });
    else cart = await api("/api/cart/update", { item_id: id, quantity: btn.dataset.act === "inc" ? qty + 1 : qty - 1 });
    updateCartBadges(cart);
    renderCartPage(cart);
  } catch (err) {
    toast(err.message, "error");
    btn.disabled = false;
  }
});

refreshCart();
