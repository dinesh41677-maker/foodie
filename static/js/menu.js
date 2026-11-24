/* Menu page: VEG / NON-VEG tabs, search, filters */
(() => {
  const app = document.getElementById("menu-app");
  const grid = document.getElementById("food-grid");
  const empty = document.getElementById("empty-state");
  const count = document.getElementById("result-count");
  const search = document.getElementById("search");
  const price = document.getElementById("price-filter");
  const category = document.getElementById("category-filter");
  const sort = document.getElementById("sort-filter");

  const state = { type: app.dataset.startType || "veg", bestseller: false, rating: false };
  let timer = null, requestNo = 0;

  function cardHtml(f) {
    const off = f.original_price > f.discounted_price
      ? Math.round((1 - f.discounted_price / f.original_price) * 100) : 0;
    return `
    <article class="card">
      <div class="card-info">
        <div class="card-top"><span class="diet ${f.food_type}" title="${f.food_type === "veg" ? "Vegetarian" : "Non-vegetarian"}"></span>
          ${f.is_bestseller ? '<span class="best">★ Bestseller</span>' : ""}</div>
        <h3>${esc(f.name)}</h3>
        <div class="price-row">
          <span class="now">${rupee(f.discounted_price)}</span>
          ${off ? `<span class="was">${rupee(f.original_price)}</span><span class="off">${off}% off</span>` : ""}
        </div>
        <span class="rate">★ ${Number(f.rating).toFixed(1)}</span>
        <p class="desc">${esc(f.description)}</p>
      </div>
      <div class="card-media">
        <img src="${esc(f.image_url)}" alt="${esc(f.name)}" loading="lazy" onerror="imgFallback(this)">
        <button class="add-btn" type="button" data-add="${f.id}" aria-label="Add ${esc(f.name)}">ADD</button>
      </div>
    </article>`;
  }

  async function load() {
    const mine = ++requestNo;
    const p = new URLSearchParams({ type: state.type });
    if (search.value.trim()) p.set("q", search.value.trim());
    if (state.bestseller) p.set("bestseller", "1");
    if (state.rating) p.set("min_rating", "4");
    if (price.value) p.set("max_price", price.value);
    if (category.value) p.set("category", category.value);
    if (sort.value) p.set("sort", sort.value);

    grid.innerHTML = '<div class="skeleton"></div><div class="skeleton"></div>';
    try {
      const data = await api("/api/menu?" + p.toString());
      if (mine !== requestNo) return;       // an older request finished late: ignore it
      grid.innerHTML = data.items.map(cardHtml).join("");
      empty.hidden = data.count > 0;
      count.textContent = data.count ? `${data.count} dish${data.count === 1 ? "" : "es"}` : "";
    } catch (err) {
      grid.innerHTML = "";
      empty.hidden = true;
      toast(err.message, "error");
    }
  }

  function syncUi() {
    document.querySelectorAll(".type-tab").forEach((t) => t.setAttribute("aria-selected", String(t.dataset.type === state.type)));
    document.querySelector('[data-filter="bestseller"]').setAttribute("aria-pressed", String(state.bestseller));
    document.querySelector('[data-filter="rating"]').setAttribute("aria-pressed", String(state.rating));
  }

  document.querySelectorAll(".type-tab").forEach((tab) => tab.addEventListener("click", () => {
    state.type = tab.dataset.type; syncUi(); load();
    history.replaceState(null, "", state.type === "nonveg" ? "/?type=nonveg" : "/");
  }));
  document.querySelectorAll(".chip").forEach((chip) => chip.addEventListener("click", () => {
    state[chip.dataset.filter] = !state[chip.dataset.filter]; syncUi(); load();
  }));
  [price, category, sort].forEach((el) => el.addEventListener("change", load));
  search.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(load, 300); });
  document.getElementById("clear-filters").addEventListener("click", () => {
    search.value = ""; price.value = ""; category.value = ""; sort.value = "";
    state.bestseller = false; state.rating = false; syncUi(); load();
  });
  grid.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-add]");
    if (btn) AddonModal.open(Number(btn.dataset.add));
  });

  syncUi();
  load();
})();
