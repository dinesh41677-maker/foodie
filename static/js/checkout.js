/* Checkout page: show the new-address fields only when needed, check before sending */
(() => {
  const form = document.getElementById("checkout-form");
  const newBox = document.getElementById("new-address");

  function syncAddress() {
    const chosen = form.querySelector('input[name="address_id"]:checked');
    newBox.hidden = !(chosen && chosen.value === "new");
  }
  form.querySelectorAll('input[name="address_id"]').forEach((r) => r.addEventListener("change", syncAddress));
  syncAddress();

  form.addEventListener("submit", (e) => {
    const errors = [];
    if (form.customer_name.value.trim().length < 2) errors.push("Enter your name.");
    if (!/^[6-9]\d{9}$/.test(form.phone.value.trim())) errors.push("Enter a valid 10 digit contact number.");
    const chosen = form.querySelector('input[name="address_id"]:checked');
    if (!chosen) errors.push("Choose a delivery address.");
    else if (chosen.value === "new") {
      if (form.address_line.value.trim().length < 5) errors.push("Enter the full delivery address.");
      if (form.city.value.trim().length < 2) errors.push("Enter the city.");
      if (!/^\d{6}$/.test(form.pincode.value.trim())) errors.push("Enter a valid 6 digit pincode.");
    }
    if (!form.querySelector('input[name="payment_method"]:checked')) errors.push("Choose a payment method.");
    if (errors.length) { e.preventDefault(); toast(errors[0], "error"); return; }
    form.querySelector('button[type="submit"]').disabled = true;   // stop double clicks
  });
})();
