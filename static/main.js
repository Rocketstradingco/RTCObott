document.addEventListener('DOMContentLoaded', () => {
  const title = document.querySelector('input[name="title"]');
  const desc = document.querySelector('textarea[name="description"]');
  const btnLabel = document.querySelector('input[name="button_label"]');
  const pTitle = document.getElementById('p-title');
  const pDesc = document.getElementById('p-desc');
  const pButton = document.getElementById('p-button');
  function update() {
    pTitle.textContent = title.value;
    pDesc.textContent = desc.value;
    pButton.textContent = btnLabel.value;
  }
  [title, desc, btnLabel].forEach(el => el && el.addEventListener('input', update));
  update();
});
