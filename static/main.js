let button = document.querySelector('.btn');
let uploadArea = document.querySelector('.drop-area');
let filesArea = document.querySelector('.uploaded-files');
let errorMsg = document.querySelector('.error-msg');
let firstFile = document.querySelector('#first-file-name');
let secondFile = document.querySelector('#second-file-name');

uploadArea.addEventListener('click', e => document.querySelector('#upload').click());

uploadArea.addEventListener('dragover', e => {
  e.preventDefault();
  uploadArea.classList.add('drop-area__over')
});

['dragleave', 'dragend'].forEach(type =>{
  uploadArea.addEventListener(type, e => uploadArea.classList.remove('drop-area__over'));
});

uploadArea.addEventListener('drop', async (e) => {
  try {
    e.preventDefault();
    if (e.dataTransfer.files.length == 2) {
      const formData = new FormData();

      for (let i = 0; i < e.dataTransfer.files.length; i++) {
        formData.append(e.dataTransfer.files[i].name, e.dataTransfer.files[i]);
      }

      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      if (response) {
        console.log('Upload completed');
      }

      firstFile.textContent = e.dataTransfer.files[0].name;
      secondFile.textContent = e.dataTransfer.files[1].name;
      uploadArea.style.display = 'none';
      filesArea.style.display = 'flex';

    } else {
      uploadArea.classList.remove('drop-area__over');
      errorMsg.style.display = 'block';
      setTimeout(() => errorMsg.style.display = 'none', 3000);
    }
  } catch (error) {
    console.log(error);
  }
});

button.addEventListener('click', () => alert('Hello!'));