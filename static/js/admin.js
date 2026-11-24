/* Admin: confirm before delete, preview chosen image */
document.addEventListener("submit", (e) => {
  const message = e.target.dataset && e.target.dataset.confirm;
  if (message && !window.confirm(message)) e.preventDefault();
});

const imageInput = document.getElementById("image-input");
if (imageInput) {
  imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    const preview = document.getElementById("image-preview");
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      toast("Image must be smaller than 2 MB.", "error");
      imageInput.value = "";
      return;
    }
    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
  });
}
