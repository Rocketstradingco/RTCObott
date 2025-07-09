document.addEventListener('DOMContentLoaded', () => {
  const title = document.querySelector('input[name="title"]');
  const desc = document.querySelector('textarea[name="description"]');
  const btnLabel = document.querySelector('input[name="button_label"]');
  const color = document.querySelector('input[name="color"]');
  const thumbnail = document.querySelector('input[name="thumbnail"]');
  const image = document.querySelector('input[name="image"]');
  const footer = document.querySelector('input[name="footer"]');
  const pTitle = document.getElementById('p-title');
  const pDesc = document.getElementById('p-desc');
  const pButton = document.getElementById('p-button');
  const pThumb = document.getElementById('p-thumb');
  const pImage = document.getElementById('p-image');
  const pFooter = document.getElementById('p-footer');
  function update() {
    pTitle.textContent = title.value;
    pDesc.textContent = desc.value;
    pButton.textContent = btnLabel.value;
    pButton.style.background = color.value;
    document.getElementById('preview').style.borderColor = color.value;
    if (thumbnail.value) {
      pThumb.src = thumbnail.value;
      pThumb.style.display = 'block';
    } else {
      pThumb.style.display = 'none';
    }
    if (image.value) {
      pImage.src = image.value;
      pImage.style.display = 'block';
    } else {
      pImage.style.display = 'none';
    }
    pFooter.textContent = footer.value;
  }
  [title, desc, btnLabel, color, thumbnail, image, footer].forEach(el => el && el.addEventListener('input', update));
  update();
});
