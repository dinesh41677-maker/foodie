/* Add-on popup: opens when ADD is pressed */
const AddonModal = (() => {
  const modal = document.getElementById("addon-modal");
  const list = document.getElementById("am-list");
  const allBox = document.getElementById("am-all");
  let food = null, qty = 1;

  const selectedIds = () => [...list.querySelectorAll("input:checked")].map((i) => Number(i.value));

  function recalc() {
    const extras = [...list.querySelectorAll("input:checked")].reduce((s, i) => s + Number(i.dataset.price), 0);
    document.getElementById("am-total").textContent = "· " + rupee((food.discounted_price + extras) * qty);
    document.getElementById("am-qty").textContent = qty;
    const boxes = list.querySelectorAll("input");
    allBox.checked = boxes.length > 0 && [...boxes].every((i) => i.checked);
  }

  function close() { modal.hidden = true; document.body.style.overflow = ""; food = null; }

  async function submit(addonIds) {
    const addBtn = document.getElementById("am-add"), skipBtn = document.getElementById("am-skip");
    addBtn.disabled = skipBtn.disabled = true;
    try {
      const cart = await api("/api/cart/add", { food_id: food.id, quantity: qty, addon_ids: addonIds });
      updateCartBadges(cart);
      toast(`${food.name} added to cart`);
      close();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      addBtn.disabled = skipBtn.disabled = false;
    }
  }

  async function open(foodId) {
    let data;
    try { data = await api("/api/foods/" + foodId); }
    catch (err) { toast(err.message, "error"); return; }
    food = data;
    qty = 1;

    if (!data.addons.length) {          // nothing to choose: add straight away
      await submit([]);
      return;
    }
    document.getElementById("am-title").textContent = data.name;
    const img = document.getElementById("am-img");
    img.src = data.image_url; img.onerror = () => imgFallback(img);
    document.getElementById("am-diet").className = "diet " + data.food_type;
    document.getElementById("am-now").textContent = rupee(data.discounted_price);
    document.getElementById("am-was").textContent = data.original_price > data.discounted_price ? rupee(data.original_price) : "";
    list.innerHTML = data.addons.map((a) => `
      <li><label><input type="checkbox" value="${a.id}" data-price="${a.price}">
        <span>${esc(a.name)}</span><span class="ap">+ ${rupee(a.price)}</span></label></li>`).join("");
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    recalc();
    document.getElementById("am-add").focus();
  }

  list.addEventListener("change", recalc);
  allBox.addEventListener("change", () => { list.querySelectorAll("input").forEach((i) => (i.checked = allBox.checked)); recalc(); });
  document.getElementById("am-plus").addEventListener("click", () => { if (qty < 20) { qty++; recalc(); } });
  document.getElementById("am-minus").addEventListener("click", () => { if (qty > 1) { qty--; recalc(); } });
  document.getElementById("am-skip").addEventListener("click", () => submit([]));
  document.getElementById("am-add").addEventListener("click", () => submit(selectedIds()));
  modal.querySelectorAll("[data-close]").forEach((el) => el.addEventListener("click", close));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !modal.hidden) close(); });

  return { open };
})();
