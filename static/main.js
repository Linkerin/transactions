// Files upload process
let analyzeBtn = document.querySelector('#analyzeBtn');
let dropAreaContainer = document.querySelector('.drop-area-container');
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
let popupCompleted = document.querySelector('#popup-completed');
let popupCompletedCloseBtn = document.querySelector('.popup-completed__closeBtn');
let popupCompletedDownloadBtn = document.querySelector('#popup-completed__downloadBtn');
let popupLoader = document.querySelector('#analysisLoader');
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
    if (files.length >= 2) {
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
      }
    } else {
      uploadArea.classList.remove('drop-area__over');
      uploadAreaText.classList.remove('drop-area__over-text');
      errorMsgContainer.style.visibility = 'visible';
      errorMsg.innerHTML = `Необходимо загрузить файлы:
                            <br>проводки, контракты, контрагенты (опционально)`;
      setTimeout(() => errorMsgContainer.style.visibility = 'hidden', 6000);
    }
  } catch (error) {
  console.log(error);
  }
}

function startPage() {
  document.body.removeChild(document.querySelector('.resultsDownloadLink'));
  filesToAnalyse.filenames = [];
  popupBackground.style.display = 'none';
  popupCompleted.classList.remove('display-flex');
  dropAreaContainer.style.visibility = 'visible'
  uploadedFilesArea.classList.remove('display-flex');
  analyzeBtn.classList.remove('active-btn');
  uploadArea.classList.remove('display-none', 'drop-area__over');
  uploadAreaText.classList.remove('drop-area__over-text');
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
    uploadAreaText.classList.remove('drop-area__over-text');
  });
});

uploadArea.addEventListener('drop', fileUpload)

uploadArea.addEventListener('click', e => dropAreaClick.click());
dropAreaClick.addEventListener('change', fileUpload)

analyzeBtn.addEventListener('click', async (e) => {
  e.preventDefault();
  if (analyzeBtn.classList.contains('active-btn')) {
    if (filesToAnalyse.filenames.length) {
      dropAreaContainer.style.visibility = 'hidden'
      popupBackground.style.display = 'block';
      popupAnalyzing.classList.add('display-flex');
      setInterval(() => {
        popupLoader.style.marginRight = '0';
        popupLoader.style.marginLeft = '380px';
        setTimeout(() => {
          popupLoader.style.marginRight = '380px';
          popupLoader.style.marginLeft = '0';
        }, 1200);
      }, 2400);
      try {
        await fetch('/pandas_upload', {
          method: 'POST',
          body: JSON.stringify(filesToAnalyse)
        }).then(async (response) => {
          if (response.ok) {
            return response.blob();
          } else {
            let msg = await response.json();
            popupBackground.style.display = 'none';
            popupAnalyzing.classList.remove('display-flex');
            dropAreaContainer.style.visibility = 'visible';
            uploadedFilesArea.classList.remove('display-flex');
            analyzeBtn.classList.remove('active-btn');
            uploadArea.classList.remove('display-none', 'drop-area__over');
            uploadAreaText.classList.remove('drop-area__over-text');
            errorMsg.innerHTML = msg.status;
            errorMsgContainer.style.visibility = 'visible';
            filesToAnalyse.filenames = [];
            setTimeout(() => errorMsgContainer.style.visibility = 'hidden', 6000);
          }
        }).then (blob => {
          const a = document.createElement("a");
          a.classList.add('resultsDownloadLink');
          a.href = window.URL.createObjectURL(blob);
          a.download = "result.xlsx";
          document.body.appendChild(a);
          popupAnalyzing.classList.remove('display-flex');
          popupCompleted.classList.add('display-flex');
        });
      } catch (error) {
        console.log(error);
      }
    } else {
      popupBackground.style.display = 'none';
      popupAnalyzing.classList.remove('display-flex');
      dropAreaContainer.style.visibility = 'visible'
      uploadedFilesArea.classList.remove('display-flex');
      analyzeBtn.classList.remove('active-btn');
      uploadArea.classList.remove('display-none', 'drop-area__over');
      uploadAreaText.classList.remove('drop-area__over-text');
      errorMsgContainer.style.visibility = 'visible';
      errorMsg.innerHTML = 'Файлы не были загружены на сервер';
      setTimeout(() => errorMsgContainer.style.visibility = 'hidden', 6000);
    }
  }
});

popupCompletedDownloadBtn.addEventListener('click', (e) => {
  e.preventDefault();
  let result = document.querySelector('.resultsDownloadLink');
  result.click();
});
popupCompletedCloseBtn.addEventListener('click', startPage);

// Information sidebar
let infoOpenBtn = document.querySelector('.info-icon');
let infoCloseBtn = document.querySelector('.info-block__closeBtn');
let infoBlock = document.querySelector('.info-block');

infoOpenBtn.addEventListener('click', () => {
  infoBlock.style.maxWidth = '400px';
  dropAreaContainer.style.paddingRight = '400px';
  infoOpenBtn.style.visibility = 'hidden';
});

infoCloseBtn.addEventListener('click', () => {
  infoBlock.style.maxWidth = '0';
  dropAreaContainer.style.paddingRight = '0';
  infoOpenBtn.style.visibility = 'visible';
});
