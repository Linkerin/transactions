// Files upload process
let button = document.querySelector('.btn');
let uploadArea = document.querySelector('.drop-area');
let filesArea = document.querySelector('.uploaded-files');
let filesAreaClick = document.querySelector('#upload')
let errorMsg = document.querySelector('.error-msg');
let firstFile = document.querySelector('#first-file-name');
let secondFile = document.querySelector('#second-file-name');
let filesToAnalyse = {filenames: []};

async function fileUpload(e) {
  let files;
  if (e.type === 'change') {
    files = e.target.files;
  } else if (e.type === 'drop') {
    files = e.dataTransfer.files;
  }

  try {
    e.preventDefault();
    if (files.length == 2) {
      const formData = new FormData();

      for (let i = 0; i < files.length; i++) {
        formData.append(files[i].name, files[i]);
      }

      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      }).then(res => res.json());

      firstFile.textContent = files[0].name;
      secondFile.textContent = files[1].name;
      uploadArea.style.display = 'none';
      filesArea.style.display = 'flex';
      
      if (response.status === 'Upload completed') {
        filesToAnalyse.filenames = response.filenames;
    } else {
      uploadArea.classList.remove('drop-area__over');
      errorMsg.style.display = 'block';
      setTimeout(() => errorMsg.style.display = 'none', 3000);
    }
  }
  } catch (error) {
  console.log(error);
  }
}

uploadArea.addEventListener('dragover', e => {
  e.preventDefault();
  uploadArea.classList.add('drop-area__over')
});

['dragleave', 'dragend'].forEach(type =>{
  uploadArea.addEventListener(type, e => uploadArea.classList.remove('drop-area__over'));
});

uploadArea.addEventListener('drop', fileUpload)

uploadArea.addEventListener('click', e => filesAreaClick.click());
filesAreaClick.addEventListener('change', fileUpload)

button.addEventListener('click', async (e) => {
  e.preventDefault();
  if (filesToAnalyse.filenames.length) {
    try {
      const pandas = await fetch('/pandas_upload', {
        method: 'POST',
        body: JSON.stringify(filesToAnalyse)
      }).then(async (response) => {
        if (response.ok) {
          return response.blob();
        } else {
          let msg = await response.json();
          errorMsg.textContent = msg.status;
          errorMsg.style.display = 'block';
          setTimeout(() => errorMsg.style.display = 'none', 2000);
        }
      }).then (blob => {
        const a = document.createElement("a");
        a.href = window.URL.createObjectURL(blob);
        a.download = "result.xlsx";
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
    } catch (error) {
      console.log(error);
    }
  } else {
    errorMsg.textContent = 'Файлы не были загружены на сервер';
    errorMsg.style.display = 'block';
    setTimeout(() => errorMsg.style.display = 'none', 3500);
  }
});

// Information sidebar
let info = document.querySelector('.info-icon')

info.addEventListener('click', () => {
  if (info.innerHTML === '<p>i</p>') {
    info.innerHTML = '<p>X</p>';
  } else {
    info.innerHTML = '<p>i</p>';
  }
})