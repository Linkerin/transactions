// Files upload process
let analyzeBtn = document.querySelector('#analyzeBtn');
let uploadArea = document.querySelector('.drop-area');
let uploadAreaText = document.querySelector('.drop-area__text');
let filesArea = document.querySelector('.uploaded-files');
let dropAreaClick = document.querySelector('#upload');
let uploadedFilesArea = document.querySelector('.drop-area-uploaded');
let uploadedFilesDesc = document.querySelector('.drop-area-uploaded__content-container');
let errorMsgContainer = document.querySelector('.error-msg-container');
let errorMsg = document.querySelector('.error-msg');
let popupBackground = document.querySelector('.popup-background');
let popupUploading = document.querySelector('#popup-uploading');
let popupAnalyzing = document.querySelector('#popup-analyzing');
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

      popupBackground.style.display = 'block';
      popupUploading.classList.add('display-flex');

      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      }).then(res => res.json());

      let uploadedFilesInfo = "";
      Array.from(files).forEach(file => {
        let fileIcon;
        let extension = file.name.split('.');
        extension = extension[extension.length - 1];
        console.log(extension)
        if (extension === 'xls' || extension === 'xlsx') {
          fileIcon = 'excel_icon.svg';
        } else {
          fileIcon = 'file_icon.svg';
        }

        uploadedFilesInfo += `
        <div class="drop-area-uploaded__content">
        <img src="/static/assets/${fileIcon}" alt="File icon">
        <p>${file.name}</p>
        </div>`;
      });
      uploadedFilesDesc.innerHTML = uploadedFilesInfo;

      popupBackground.style.display = 'none';
      popupUploading.classList.remove('display-flex');

      if (response.status === 'Upload completed') {
        filesToAnalyse.filenames = response.filenames;
        uploadArea.classList.add('display-none');
        uploadedFilesArea.classList.add('display-flex');
        analyzeBtn.classList.add('active-btn');
    } else {
      uploadArea.classList.remove('drop-area__over');
      uploadAreaText.classList.remove('drop-area__over-text');
      errorMsgContainer.style.visibility = 'visible';
      errorMsg.innerHTML = 'Необходимо загрузить 2 файла:<br>проводки и контракты';
      setTimeout(() => errorMsgContainer.style.visibility = 'hidden', 5000);
    }
  }
  } catch (error) {
  console.log(error);
  }
}

uploadArea.addEventListener('dragover', e => {
  e.preventDefault();
  uploadArea.classList.add('drop-area__over');
  uploadAreaText.classList.add('drop-area__over-text');
});

['dragleave', 'dragend'].forEach(type =>{
  uploadArea.addEventListener(type, e => {
    uploadArea.classList.remove('drop-area__over');
    uploadAreaText.classList.remove('drop-area__over-text');
  });
});

uploadArea.addEventListener('drop', fileUpload)

uploadArea.addEventListener('click', e => dropAreaClick.click());
dropAreaClick.addEventListener('change', fileUpload)

analyzeBtn.addEventListener('click', async (e) => {
  e.preventDefault();
  if (filesToAnalyse.filenames.length) {
    popupBackground.style.display = 'block';
    popupAnalyzing.classList.add('display-flex');
    try {
      await fetch('/pandas_upload', {
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
let infoOpenBtn = document.querySelector('.info-icon');
let infoCloseBtn = document.querySelector('.info-block__closeBtn');
let infoBlock = document.querySelector('.info-block');

infoOpenBtn.addEventListener('click', () => {
  infoBlock.style.display = 'flex';
  infoOpenBtn.style.visibility = 'hidden';
});

infoCloseBtn.addEventListener('click', () => {
  infoBlock.style.display = 'none';
  infoOpenBtn.style.visibility = 'visible';
});