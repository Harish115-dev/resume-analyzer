document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("resume");
  const fileChosen = document.getElementById("file-chosen");
  const form = document.getElementById("analyze-form");
  const submitBtn = document.getElementById("submit-btn");
  const submitText = document.getElementById("submit-text");

  if (!dropzone || !fileInput) return;

  function showChosenFile(file) {
    if (file) {
      fileChosen.textContent = "→ " + file.name;
    }
  }

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      showChosenFile(fileInput.files[0]);
    }
  });

  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("drag");
    })
  );

  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("drag");
    })
  );

  dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      showChosenFile(fileInput.files[0]);
    }
  });

  form.addEventListener("submit", () => {
    if (!fileInput.files.length) return; // let native validation handle it
    submitBtn.disabled = true;
    submitText.textContent = "Analyzing...";
  });
});